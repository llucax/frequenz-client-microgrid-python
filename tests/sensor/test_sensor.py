# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Tests for the Sensor class."""

from datetime import datetime, timedelta, timezone

import pytest
from frequenz.client.common.microgrid import MicrogridId
from frequenz.client.common.microgrid.sensors import SensorId

from frequenz.client.microgrid import Lifetime
from frequenz.client.microgrid.sensor import Sensor


@pytest.fixture
def now() -> datetime:
    """Get the current time."""
    return datetime.now(timezone.utc)


def test_sensor_creation_defaults() -> None:
    """Test Sensor defaults are as expected."""
    sensor = Sensor(id=SensorId(1), microgrid_id=MicrogridId(1))

    assert sensor.id == SensorId(1)
    assert sensor.microgrid_id == MicrogridId(1)
    assert sensor.name is None
    assert sensor.manufacturer is None
    assert sensor.model_name is None
    assert sensor.operational_lifetime == Lifetime()


def test_sensor_creation_full(now: datetime) -> None:
    """Test Sensor creation with all fields."""
    start = now
    end = start + timedelta(days=1)
    sensor = Sensor(
        id=SensorId(1),
        microgrid_id=MicrogridId(2),
        name="test-sensor",
        manufacturer="Test Manufacturer",
        model_name="Test Model",
        operational_lifetime=Lifetime(
            start=start,
            end=end,
        ),
    )

    assert sensor.id == SensorId(1)
    assert sensor.microgrid_id == MicrogridId(2)
    assert sensor.name == "test-sensor"
    assert sensor.manufacturer == "Test Manufacturer"
    assert sensor.model_name == "Test Model"
    assert sensor.operational_lifetime.start == start
    assert sensor.operational_lifetime.end == end


@pytest.mark.parametrize(
    "name,expected_str",
    [
        pytest.param(None, "<Sensor:SID1>", id="no_name"),
        pytest.param("test-sensor", "<Sensor:SID1:test-sensor>", id="with_name"),
    ],
)
def test_sensor_str(name: str | None, expected_str: str) -> None:
    """Test string representation of a sensor."""
    sensor = Sensor(
        id=SensorId(1),
        microgrid_id=MicrogridId(1),
        name=name,
        manufacturer="Test Manufacturer",
        model_name="Test Model",
        operational_lifetime=Lifetime(
            start=datetime.now(timezone.utc),
            end=datetime.now(timezone.utc) + timedelta(days=1),
        ),
    )
    assert str(sensor) == expected_str


_SENSOR = Sensor(
    id=SensorId(1),
    microgrid_id=MicrogridId(1),
    name="test",
    manufacturer="Test Mfg",
    model_name="Model A",
)

_DIFFERENT_NAME = Sensor(
    id=_SENSOR.id,
    microgrid_id=_SENSOR.microgrid_id,
    name="different",
    manufacturer=_SENSOR.manufacturer,
    model_name=_SENSOR.model_name,
)

_DIFFERENT_ID = Sensor(
    id=SensorId(2),
    microgrid_id=_SENSOR.microgrid_id,
    name=_SENSOR.name,
    manufacturer=_SENSOR.manufacturer,
    model_name=_SENSOR.model_name,
)

_DIFFERENT_MICROGRID = Sensor(
    id=_SENSOR.id,
    microgrid_id=MicrogridId(2),
    name=_SENSOR.name,
    manufacturer=_SENSOR.manufacturer,
    model_name=_SENSOR.model_name,
)

_DIFFERENT_BOTH_ID = Sensor(
    id=SensorId(2),
    microgrid_id=MicrogridId(2),
    name=_SENSOR.name,
    manufacturer=_SENSOR.manufacturer,
    model_name=_SENSOR.model_name,
)


@pytest.mark.parametrize(
    "other,expected",
    [
        pytest.param(_SENSOR, True, id="self"),
        pytest.param(_DIFFERENT_NAME, False, id="other_name"),
        pytest.param(_DIFFERENT_ID, False, id="other_id"),
        pytest.param(_DIFFERENT_MICROGRID, False, id="other_microgrid"),
        pytest.param(_DIFFERENT_BOTH_ID, False, id="other_both_id"),
    ],
    ids=lambda o: str(o.id) if isinstance(o, Sensor) else str(o),
)
def test_sensor_equality(other: Sensor, expected: bool) -> None:
    """Test sensor equality."""
    assert (_SENSOR == other) is expected
    assert (other == _SENSOR) is expected
    assert (_SENSOR != other) is not expected
    assert (other != _SENSOR) is not expected


@pytest.mark.parametrize(
    "other,expected",
    [
        pytest.param(_SENSOR, True, id="self"),
        pytest.param(_DIFFERENT_NAME, True, id="other_name"),
        pytest.param(_DIFFERENT_ID, False, id="other_id"),
        pytest.param(_DIFFERENT_MICROGRID, False, id="other_microgrid"),
        pytest.param(_DIFFERENT_BOTH_ID, False, id="other_both_id"),
    ],
)
def test_sensor_identity(other: Sensor, expected: bool) -> None:
    """Test sensor identity."""
    assert (_SENSOR.identity == other.identity) is expected
    assert other.identity == (other.id, other.microgrid_id)


_ALL_SENSORS_PARAMS = [
    pytest.param(_SENSOR, id="orig"),
    pytest.param(_DIFFERENT_NAME, id="other_name"),
    pytest.param(_DIFFERENT_ID, id="other_id"),
    pytest.param(_DIFFERENT_MICROGRID, id="other_microgrid"),
    pytest.param(_DIFFERENT_BOTH_ID, id="other_both_id"),
]


@pytest.mark.parametrize("sensor1", _ALL_SENSORS_PARAMS)
@pytest.mark.parametrize("sensor2", _ALL_SENSORS_PARAMS)
def test_sensor_hash(sensor1: Sensor, sensor2: Sensor) -> None:
    """Test that the Sensor hash is consistent."""
    # We can only say the hash are the same if the sensors are equal, if they
    # are not, they could still have the same hash (and they will if they have
    # only different non-hashable attributes)
    if sensor1 == sensor2:
        assert hash(sensor1) == hash(sensor2)
