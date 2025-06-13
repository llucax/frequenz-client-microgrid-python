# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Microgrid sensor data."""

import enum
from dataclasses import dataclass
from datetime import datetime
from typing import assert_never

from frequenz.api.common.v1.microgrid.sensors import sensors_pb2
from frequenz.client.common.microgrid.sensors import SensorId

from ..metrics import AggregatedMetricValue, AggregationMethod, Metric


@enum.unique
class SensorStateCode(enum.Enum):
    """The various states that a sensor can be in."""

    UNSPECIFIED = sensors_pb2.SENSOR_STATE_CODE_UNSPECIFIED
    """Default value (this should not be normally used and usually indicates an issue)."""

    ON = sensors_pb2.SENSOR_STATE_CODE_ON
    """The sensor is up and running."""

    ERROR = sensors_pb2.SENSOR_STATE_CODE_ERROR
    """The sensor is in an error state."""


@enum.unique
class SensorErrorCode(enum.Enum):
    """The various errors that can occur in sensors."""

    UNSPECIFIED = sensors_pb2.SENSOR_ERROR_CODE_UNSPECIFIED
    """Default value (this should not be normally used and usually indicates an issue)."""

    UNKNOWN = sensors_pb2.SENSOR_ERROR_CODE_UNKNOWN
    """An unknown or an undefined error

    The error sent by the sensor doesn't fit any of the known error codes, or the
    parsing of the error failed.
    """

    INTERNAL = sensors_pb2.SENSOR_ERROR_CODE_INTERNAL
    """An internal error occurred in the sensor."""


@dataclass(frozen=True, kw_only=True)
class SensorStateSample:
    """A sample of state, warnings, and errors for a sensor at a specific time."""

    sampled_at: datetime
    """The time at which this state was sampled."""

    states: frozenset[SensorStateCode | int]
    """The set of states of the sensor.

    If the reported state is not known by the client (it could happen when using an
    older version of the client with a newer version of the server), it will be
    represented as an `int` and **not** the
    [`SensorStateCode.UNSPECIFIED`][frequenz.client.microgrid.sensor.SensorStateCode.UNSPECIFIED]
    value (this value is used only when the state is not known by the server).
    """

    warnings: frozenset[SensorErrorCode | int]
    """The set of warnings for the sensor."""

    errors: frozenset[SensorErrorCode | int]
    """The set of errors for the sensor.

    This set will only contain errors if the sensor is in an error state.
    """


@dataclass(frozen=True, kw_only=True)
class SensorMetricSample:
    """A sample of a sensor metric at a specific time.

    This represents a single sample of a specific metric, the value of which is either
    measured at a particular time.
    """

    sampled_at: datetime
    """The moment when the metric was sampled."""

    metric: Metric | int
    """The metric that was sampled."""

    value: float | AggregatedMetricValue | None
    """The value of the sampled metric."""

    def as_single_value(
        self, *, aggregation_method: AggregationMethod = AggregationMethod.AVG
    ) -> float | None:
        """Return the value of this sample as a single value.

        if [`value`][frequenz.client.microgrid.sensor.SensorMetricSample.value] is a `float`,
        it is returned as is. If `value` is an
        [`AggregatedMetricValue`][frequenz.client.microgrid.metrics.AggregatedMetricValue],
        the value is aggregated using the provided `aggregation_method`.

        Args:
            aggregation_method: The method to use to aggregate the value when `value` is
                a `AggregatedMetricValue`.

        Returns:
            The value of the sample as a single value, or `None` if the value is `None`.
        """
        match self.value:
            case float() | int():
                return self.value
            case AggregatedMetricValue():
                match aggregation_method:
                    case AggregationMethod.AVG:
                        return self.value.avg
                    case AggregationMethod.MIN:
                        return self.value.min
                    case AggregationMethod.MAX:
                        return self.value.max
                    case unexpected:
                        assert_never(unexpected)
            case None:
                return None
            case unexpected:
                assert_never(unexpected)


@dataclass(frozen=True, kw_only=True)
class SensorDataSamples:
    """An aggregate of multiple metrics, states, and errors of a sensor."""

    sensor_id: SensorId
    """The unique identifier of the sensor."""

    metric_samples: list[SensorMetricSample]
    """The metrics sampled from the sensor."""

    states: list[SensorStateSample]
    """The states sampled from the sensor."""
