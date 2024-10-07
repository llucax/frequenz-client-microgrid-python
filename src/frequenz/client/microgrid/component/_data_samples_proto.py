# License: MIT
# Copyright © 2024 Frequenz Energy-as-a-Service GmbH

"""Loading of ComponentDataSamples objects from protobuf messages."""


from frequenz.api.common.v1.microgrid.components import components_pb2

from .._id import ComponentId
from ..metrics._sample_proto import metric_sample_from_proto
from ._data_samples import ComponentDataSamples
from ._state_sample_proto import component_state_sample_from_proto


def component_data_sample_from_proto(
    message: components_pb2.ComponentData,
) -> ComponentDataSamples:
    """Convert a protobuf component data message to a component data object.

    Args:
        message: The protobuf message to convert.

    Returns:
        The resulting `ComponentDataSamples` object.
    """
    # At some point it might make sense to also log issues found in the samples, but
    # using a naive approach like in `component_from_proto` might spam the logs too
    # much, as we can receive several samples per second, and if a component is in
    # a unrecognized state for long, it will mean we will emit the same log message
    # again and again.
    return ComponentDataSamples(
        component_id=ComponentId(message.component_id),
        metrics=[metric_sample_from_proto(sample) for sample in message.metric_samples],
        states=[component_state_sample_from_proto(state) for state in message.states],
    )
