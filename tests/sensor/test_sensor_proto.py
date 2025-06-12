# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Tests for protobuf conversion of sensor and sensor data objects."""

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from unittest.mock import Mock, patch

import pytest
from frequenz.api.common.v1.microgrid import lifetime_pb2
from frequenz.api.common.v1.microgrid.sensors import sensors_pb2
from frequenz.client.common.microgrid import MicrogridId
from frequenz.client.common.microgrid.sensors import SensorId
from google.protobuf.timestamp_pb2 import Timestamp

from frequenz.client.microgrid import Lifetime
from frequenz.client.microgrid.sensor import Sensor
from frequenz.client.microgrid.sensor._sensor_proto import (
    sensor_from_proto,
    sensor_from_proto_with_issues,
)


@patch("frequenz.client.microgrid.sensor._sensor_proto.sensor_from_proto_with_issues")
def test_sensor_from_proto(
    mock_sensor_from_proto_with_issues: Mock,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test main sensor conversion from protobuf."""
    mock_proto = Mock(name="PbSensor", spec=sensors_pb2.Sensor)
    mock_sensor = Mock(name="Sensor", spec=Sensor)
    captured_major_issues: list[str] | None = None
    captured_minor_issues: list[str] | None = None

    def _fake_sensor_from_proto_with_issues(
        _: sensors_pb2.Sensor, major_issues: list[str], minor_issues: list[str]
    ) -> Sensor:
        """Fake function to simulate sensor conversion."""
        nonlocal captured_major_issues
        nonlocal captured_minor_issues
        captured_major_issues = major_issues
        captured_minor_issues = minor_issues

        major_issues.append("major issue")
        minor_issues.append("minor issue")
        return mock_sensor

    mock_sensor_from_proto_with_issues.side_effect = _fake_sensor_from_proto_with_issues

    with caplog.at_level("DEBUG"):
        sensor = sensor_from_proto(mock_proto)

    assert sensor is mock_sensor
    mock_sensor_from_proto_with_issues.assert_called_once_with(
        mock_proto,
        # We need to use the same instance here because it was mutated (it was called
        # with empty lists but they were mutated in the function)
        major_issues=captured_major_issues,
        minor_issues=captured_minor_issues,
    )
    assert captured_major_issues == ["major issue"]
    assert captured_minor_issues == ["minor issue"]
    assert len(caplog.records) == 2
    assert caplog.records[0].levelname == "WARNING"
    assert "Found issues in sensor: major issue" in caplog.records[0].message
    assert caplog.records[1].levelname == "DEBUG"
    assert "Found minor issues in sensor: minor issue" in caplog.records[1].message


@dataclass(frozen=True, kw_only=True)
class _SensorConversionTestCase:
    """Test case for sensor protobuf conversion."""

    test_id: str
    """Description of the test case."""

    proto_message: sensors_pb2.Sensor
    """The input protobuf message."""

    expected_sensor: Sensor
    """The expected Sensor object."""

    expected_major_issues: list[str] = field(default_factory=list)
    """Expected major issues during conversion."""

    expected_minor_issues: list[str] = field(default_factory=list)
    """Expected minor issues during conversion."""


_START = datetime(2023, 1, 1, tzinfo=timezone.utc)
_END = _START + timedelta(days=1)

# Test cases for sensor_from_proto_with_issues
_sensor_conversion_test_cases: list[_SensorConversionTestCase] = [
    _SensorConversionTestCase(
        test_id="full",
        proto_message=sensors_pb2.Sensor(
            id=42,
            microgrid_id=52,
            name="Test sensor",
            manufacturer="Test Manufacturer",
            model_name="Test Model",
            operational_lifetime=lifetime_pb2.Lifetime(
                start_timestamp=Timestamp(seconds=int(_START.timestamp())),
                end_timestamp=Timestamp(seconds=int(_END.timestamp())),
            ),
        ),
        expected_sensor=Sensor(
            id=SensorId(42),
            microgrid_id=MicrogridId(52),
            name="Test sensor",
            manufacturer="Test Manufacturer",
            model_name="Test Model",
            operational_lifetime=Lifetime(start=_START, end=_END),
        ),
    ),
    _SensorConversionTestCase(
        test_id="missing_fields",
        proto_message=sensors_pb2.Sensor(
            id=43,
            microgrid_id=53,
        ),
        expected_sensor=Sensor(
            id=SensorId(43),
            microgrid_id=MicrogridId(53),
            name=None,
            manufacturer=None,
            model_name=None,
            operational_lifetime=Lifetime(),
        ),
        expected_minor_issues=[
            "name is empty",
            "manufacturer is empty",
            "model_name is empty",
            "missing operational lifetime, considering it always operational",
        ],
    ),
    _SensorConversionTestCase(
        test_id="invalid_lifetime",
        proto_message=sensors_pb2.Sensor(
            id=45,
            microgrid_id=55,
            name="Test sensor",
            manufacturer="Test Manufacturer",
            model_name="Test Model",
            operational_lifetime=lifetime_pb2.Lifetime(
                start_timestamp=Timestamp(seconds=int(_END.timestamp())),
                end_timestamp=Timestamp(seconds=int(_START.timestamp())),
            ),
        ),
        expected_sensor=Sensor(
            id=SensorId(45),
            microgrid_id=MicrogridId(55),
            name="Test sensor",
            manufacturer="Test Manufacturer",
            model_name="Test Model",
            operational_lifetime=Lifetime(),  # Default due to invalid lifetime
        ),
        expected_major_issues=[
            "invalid operational lifetime (Start (2023-01-02 00:00:00+00:00) must be "
            "before or equal to end (2023-01-01 00:00:00+00:00)), considering it as "
            "missing (i.e. always operational)",
        ],
        expected_minor_issues=[],
    ),
    _SensorConversionTestCase(
        test_id="missing_fields_and_invalid_lifetime",
        proto_message=sensors_pb2.Sensor(
            id=45,
            microgrid_id=55,
            operational_lifetime=lifetime_pb2.Lifetime(
                start_timestamp=Timestamp(seconds=int(_END.timestamp())),
                end_timestamp=Timestamp(seconds=int(_START.timestamp())),
            ),
        ),
        expected_sensor=Sensor(
            id=SensorId(45),
            microgrid_id=MicrogridId(55),
            name=None,
            manufacturer=None,
            model_name=None,
            operational_lifetime=Lifetime(),
        ),
        expected_major_issues=[
            "invalid operational lifetime (Start (2023-01-02 00:00:00+00:00) must be "
            "before or equal to end (2023-01-01 00:00:00+00:00)), considering it as "
            "missing (i.e. always operational)",
        ],
        expected_minor_issues=[
            "name is empty",
            "manufacturer is empty",
            "model_name is empty",
        ],
    ),
]


@pytest.mark.parametrize("case", _sensor_conversion_test_cases, ids=lambda c: c.test_id)
def test_sensor_from_proto_with_issues(case: _SensorConversionTestCase) -> None:
    """Test sensor conversion from protobuf with issue collection."""
    major_issues: list[str] = []
    minor_issues: list[str] = []

    sensor = sensor_from_proto_with_issues(
        case.proto_message,
        major_issues=major_issues,
        minor_issues=minor_issues,
    )

    assert sensor == case.expected_sensor
    assert sorted(major_issues) == sorted(case.expected_major_issues)
    assert sorted(minor_issues) == sorted(case.expected_minor_issues)
