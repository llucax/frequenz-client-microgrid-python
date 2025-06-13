# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Loading of SensorDataSamples objects from protobuf messages."""

from functools import partial

from frequenz.api.common.v1.microgrid.sensors import sensors_pb2
from frequenz.client.base import conversion
from frequenz.client.common.microgrid.sensors import SensorId

from frequenz.client.microgrid.metrics._sample_proto import (
    metric_value_variant_from_proto,
)

from .._util import enum_from_proto
from ..metrics import Metric
from ._data import (
    SensorDataSamples,
    SensorErrorCode,
    SensorMetricSample,
    SensorStateCode,
    SensorStateSample,
)

_state_from_proto = partial(enum_from_proto, enum_type=SensorStateCode)
_error_from_proto = partial(enum_from_proto, enum_type=SensorErrorCode)


def sensor_data_samples_from_proto(
    message: sensors_pb2.SensorData,
) -> SensorDataSamples:
    """Convert a protobuf component data message to a sensor data object."""
    return SensorDataSamples(
        sensor_id=SensorId(message.sensor_id),
        metric_samples=list(
            map(sensor_metric_sample_from_proto, message.metric_samples)
        ),
        states=list(map(sensor_state_sample_from_proto, message.states)),
    )


def sensor_metric_sample_from_proto(
    message: sensors_pb2.SensorMetricSample,
) -> SensorMetricSample:
    """Convert a protobuf message to a `SensorMetricSample` object."""
    return SensorMetricSample(
        sampled_at=conversion.to_datetime(message.sampled_at),
        metric=enum_from_proto(message.metric, Metric),
        value=metric_value_variant_from_proto(message.value),
    )


def sensor_state_sample_from_proto(
    message: sensors_pb2.SensorState,
) -> SensorStateSample:
    """Convert a protobuf message to a `SensorStateSample` object."""
    return SensorStateSample(
        sampled_at=conversion.to_datetime(message.sampled_at),
        states=frozenset(map(_state_from_proto, message.states)),
        # This version of the API doesn't include warnings, so we use an empty set.
        # We keep the field because future versions will include warnings.
        warnings=frozenset(),
        errors=frozenset(map(_error_from_proto, message.errors)),
    )
