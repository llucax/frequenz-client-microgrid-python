# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Tests for protobuf conversion of sensor data objects."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Final

import pytest
from frequenz.api.common.v1.metrics import metric_sample_pb2
from frequenz.api.common.v1.microgrid.sensors import sensors_pb2
from frequenz.client.base import conversion
from frequenz.client.common.microgrid.sensors import SensorId
from google.protobuf.timestamp_pb2 import Timestamp

from frequenz.client.microgrid.metrics import AggregatedMetricValue, Metric
from frequenz.client.microgrid.sensor import (
    SensorDataSamples,
    SensorErrorCode,
    SensorMetricSample,
    SensorStateCode,
    SensorStateSample,
)
from frequenz.client.microgrid.sensor._data_proto import (
    sensor_data_samples_from_proto,
    sensor_metric_sample_from_proto,
    sensor_state_sample_from_proto,
)


@pytest.fixture
def now() -> datetime:
    """Return a fixed datetime object for testing."""
    return datetime.now(timezone.utc)


@pytest.fixture
def sensor_id() -> SensorId:
    """Provide a test sensor ID."""
    return SensorId(42)


DATETIME: Final[datetime] = datetime(2023, 3, 15, 12, 0, 0, tzinfo=timezone.utc)
TIMESTAMP: Final[Timestamp] = Timestamp(seconds=int(DATETIME.timestamp()))


@dataclass(frozen=True, kw_only=True)
class _SensorMetricSampleConversionTestCase:
    """Test case for SensorMetricSample protobuf conversion."""

    name: str
    """The description of the test case."""

    proto: sensors_pb2.SensorMetricSample
    """The input protobuf message."""

    expected_sample: SensorMetricSample
    """The expected MetricSample object."""


@pytest.mark.parametrize(
    "case",
    [
        _SensorMetricSampleConversionTestCase(
            name="simple_value",
            proto=sensors_pb2.SensorMetricSample(
                sampled_at=TIMESTAMP,
                metric=Metric.AC_ACTIVE_POWER.value,
                value=metric_sample_pb2.MetricValueVariant(
                    simple_metric=metric_sample_pb2.SimpleMetricValue(value=5.0)
                ),
            ),
            expected_sample=SensorMetricSample(
                sampled_at=DATETIME,
                metric=Metric.AC_ACTIVE_POWER,
                value=5.0,
            ),
        ),
        _SensorMetricSampleConversionTestCase(
            name="aggregated_value",
            proto=sensors_pb2.SensorMetricSample(
                sampled_at=TIMESTAMP,
                metric=Metric.AC_ACTIVE_POWER.value,
                value=metric_sample_pb2.MetricValueVariant(
                    aggregated_metric=metric_sample_pb2.AggregatedMetricValue(
                        avg_value=5.0, min_value=1.0, max_value=10.0
                    )
                ),
            ),
            expected_sample=SensorMetricSample(
                sampled_at=DATETIME,
                metric=Metric.AC_ACTIVE_POWER,
                value=AggregatedMetricValue(avg=5.0, min=1.0, max=10.0, raw_values=[]),
            ),
        ),
        _SensorMetricSampleConversionTestCase(
            name="no_value",
            proto=sensors_pb2.SensorMetricSample(
                sampled_at=TIMESTAMP,
                metric=Metric.AC_ACTIVE_POWER.value,
            ),
            expected_sample=SensorMetricSample(
                sampled_at=DATETIME,
                metric=Metric.AC_ACTIVE_POWER,
                value=None,
            ),
        ),
        _SensorMetricSampleConversionTestCase(
            name="unrecognized_metric",
            proto=sensors_pb2.SensorMetricSample(
                sampled_at=TIMESTAMP,
                metric=999,  # type: ignore[arg-type]
                value=metric_sample_pb2.MetricValueVariant(
                    simple_metric=metric_sample_pb2.SimpleMetricValue(value=5.0)
                ),
            ),
            expected_sample=SensorMetricSample(
                sampled_at=DATETIME, metric=999, value=5.0
            ),
        ),
    ],
    ids=lambda case: case.name,
)
def test_sensor_metric_sample_from_proto_with_issues(
    case: _SensorMetricSampleConversionTestCase,
) -> None:
    """Test conversion from protobuf message to SensorMetricSample."""
    sample = sensor_metric_sample_from_proto(case.proto)

    assert sample == case.expected_sample


@dataclass(frozen=True, kw_only=True)
class _SensorStateSampleTestCase:
    """Test case for sensor_state_sample_from_proto."""

    test_id: str
    states: list[sensors_pb2.SensorStateCode.ValueType] = field(default_factory=list)
    errors: list[sensors_pb2.SensorErrorCode.ValueType] = field(default_factory=list)
    expected_states: frozenset[SensorStateCode | int]
    expected_errors: frozenset[SensorErrorCode | int]
    expected_warnings: frozenset[SensorErrorCode | int]


@pytest.mark.parametrize(
    "case",
    [
        _SensorStateSampleTestCase(
            test_id="state_on-error_empty",
            states=[sensors_pb2.SENSOR_STATE_CODE_ON],
            expected_states=frozenset([SensorStateCode.ON]),
            expected_errors=frozenset(),
            expected_warnings=frozenset(),
        ),
        _SensorStateSampleTestCase(
            test_id="state_error-error_internal",
            states=[sensors_pb2.SENSOR_STATE_CODE_ERROR],
            errors=[sensors_pb2.SENSOR_ERROR_CODE_INTERNAL],
            expected_states=frozenset([SensorStateCode.ERROR]),
            expected_errors=frozenset([SensorErrorCode.INTERNAL]),
            expected_warnings=frozenset(),
        ),
        # No warning test case because the protocol doesn't support them in this
        # version.
        _SensorStateSampleTestCase(
            test_id="state_unknown-error_unknown",
            states=[999],  # type: ignore[list-item]
            errors=[888],  # type: ignore[list-item]
            expected_states=frozenset([999]),
            expected_errors=frozenset([888]),
            expected_warnings=frozenset(),
        ),
    ],
    ids=lambda case: case.test_id,
)
def test_sensor_state_sample_from_proto(
    case: _SensorStateSampleTestCase, now: datetime
) -> None:
    """Test conversion of state, errors, and warnings."""
    proto = sensors_pb2.SensorState(
        sampled_at=conversion.to_timestamp(now), states=case.states, errors=case.errors
    )

    result = sensor_state_sample_from_proto(proto)

    assert isinstance(result, SensorStateSample)
    assert result.sampled_at == now
    assert result.states == case.expected_states
    assert result.errors == case.expected_errors
    assert result.warnings == case.expected_warnings


@dataclass(frozen=True, kw_only=True)
class _SensorDataSamplesTestCase:  # pylint: disable=too-many-instance-attributes
    """Test case for sensor_data_samples_from_proto."""

    test_id: str
    proto: sensors_pb2.SensorData
    expected_data: SensorDataSamples


@pytest.mark.parametrize(
    "case",
    [
        _SensorDataSamplesTestCase(
            test_id="full",
            proto=sensors_pb2.SensorData(
                sensor_id=42,
                metric_samples=[
                    sensors_pb2.SensorMetricSample(
                        sampled_at=TIMESTAMP,
                        metric=metric_sample_pb2.METRIC_SENSOR_TEMPERATURE,
                        value=metric_sample_pb2.MetricValueVariant(
                            simple_metric=metric_sample_pb2.SimpleMetricValue(
                                value=20.0
                            )
                        ),
                    )
                ],
                states=[
                    sensors_pb2.SensorState(
                        sampled_at=TIMESTAMP,
                        states=[sensors_pb2.SENSOR_STATE_CODE_ON],
                        errors=[sensors_pb2.SENSOR_ERROR_CODE_UNKNOWN],
                    )
                ],
            ),
            expected_data=SensorDataSamples(
                sensor_id=SensorId(42),
                metric_samples=[
                    SensorMetricSample(
                        sampled_at=DATETIME,
                        metric=Metric.SENSOR_TEMPERATURE,
                        value=20.0,
                    )
                ],
                states=[
                    SensorStateSample(
                        sampled_at=DATETIME,
                        states=frozenset([SensorStateCode.ON]),
                        errors=frozenset([SensorErrorCode.UNKNOWN]),
                        warnings=frozenset(),
                    )
                ],
            ),
        ),
        _SensorDataSamplesTestCase(
            test_id="empty_metric_samples",
            proto=sensors_pb2.SensorData(
                sensor_id=42,
                metric_samples=[],  # Empty metric samples
                states=[
                    sensors_pb2.SensorState(
                        sampled_at=TIMESTAMP,
                        states=[sensors_pb2.SENSOR_STATE_CODE_ON],
                        errors=[],
                    )
                ],
            ),
            expected_data=SensorDataSamples(
                sensor_id=SensorId(42),
                metric_samples=[],
                states=[
                    SensorStateSample(
                        sampled_at=DATETIME,
                        states=frozenset([SensorStateCode.ON]),
                        errors=frozenset(),
                        warnings=frozenset(),
                    )
                ],
            ),
        ),
        _SensorDataSamplesTestCase(
            test_id="empty_states",
            proto=sensors_pb2.SensorData(
                sensor_id=42,
                metric_samples=[
                    sensors_pb2.SensorMetricSample(
                        sampled_at=TIMESTAMP,
                        metric=metric_sample_pb2.METRIC_SENSOR_TEMPERATURE,
                        value=metric_sample_pb2.MetricValueVariant(
                            simple_metric=metric_sample_pb2.SimpleMetricValue(
                                value=25.5
                            )
                        ),
                    )
                ],
                states=[],  # Empty states
            ),
            expected_data=SensorDataSamples(
                sensor_id=SensorId(42),
                metric_samples=[
                    SensorMetricSample(
                        sampled_at=DATETIME,
                        metric=Metric.SENSOR_TEMPERATURE,
                        value=25.5,
                    )
                ],
                states=[],
            ),
        ),
        _SensorDataSamplesTestCase(
            test_id="empty_metric_samples_and_states",
            proto=sensors_pb2.SensorData(
                sensor_id=42,
                metric_samples=[],  # Empty metric samples
                states=[],  # Empty states
            ),
            expected_data=SensorDataSamples(
                sensor_id=SensorId(42),
                metric_samples=[],
                states=[],
            ),
        ),
    ],
    ids=lambda case: case.test_id,
)
def test_sensor_data_samples_from_proto(case: _SensorDataSamplesTestCase) -> None:
    """Test loading of SensorDataSamples."""
    result = sensor_data_samples_from_proto(case.proto)

    assert isinstance(result, SensorDataSamples)
    assert result == case.expected_data
