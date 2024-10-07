# License: MIT
# Copyright © 2024 Frequenz Energy-as-a-Service GmbH

"""Loading of MetricSample and AggregatedMetricValue objects from protobuf messages."""

from frequenz.api.common.v1.microgrid.components import components_pb2
from frequenz.client.base import conversion

from .._util import enum_from_proto
from ._state_sample import ComponentErrorCode, ComponentStateCode, ComponentStateSample


def component_state_sample_from_proto(
    message: components_pb2.ComponentState,
) -> ComponentStateSample:
    """Convert a protobuf message to a `ComponentStateSample` object.

    Args:
        message: The protobuf message to convert.

    Returns:
        The resulting `ComponentStateSample` object.
    """
    return ComponentStateSample(
        sampled_at=conversion.to_datetime(message.sampled_at),
        states=frozenset(
            enum_from_proto(s, ComponentStateCode) for s in message.states
        ),
        warnings=frozenset(
            enum_from_proto(w, ComponentErrorCode) for w in message.warnings
        ),
        errors=frozenset(
            enum_from_proto(e, ComponentErrorCode) for e in message.errors
        ),
    )
