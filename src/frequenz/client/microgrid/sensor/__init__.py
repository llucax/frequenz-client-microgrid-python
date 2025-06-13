# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Microgrid sensors.

This package provides classes and utilities for working with different types of
sensors in a microgrid environment. [`Sensor`][frequenz.client.microgrid.sensor.Sensor]s
measure various physical metrics in the surrounding environment, such as temperature,
humidity, and solar irradiance.

# Streaming Sensor Data Samples

This package also provides several data structures for handling sensor readings
and states:

* [`SensorDataSamples`][frequenz.client.microgrid.sensor.SensorDataSamples]:
    Represents a collection of sensor data samples.
* [`SensorErrorCode`][frequenz.client.microgrid.sensor.SensorErrorCode]:
    Defines error codes that a sensor can report.
* [`SensorMetricSample`][frequenz.client.microgrid.sensor.SensorMetricSample]:
    Represents a single sample of a sensor metric, including its value and
    timestamp.
* [`SensorStateCode`][frequenz.client.microgrid.sensor.SensorStateCode]:
    Defines codes representing the operational state of a sensor.
* [`SensorStateSample`][frequenz.client.microgrid.sensor.SensorStateSample]:
    Represents a single sample of a sensor's state, including its state code
    and timestamp.
"""

from ._data import (
    SensorDataSamples,
    SensorErrorCode,
    SensorMetricSample,
    SensorStateCode,
    SensorStateSample,
)
from ._sensor import Sensor

__all__ = [
    "Sensor",
    "SensorDataSamples",
    "SensorErrorCode",
    "SensorMetricSample",
    "SensorStateCode",
    "SensorStateSample",
]
