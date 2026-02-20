# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Definition of a component data aggregate."""

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime

from frequenz.client.common.microgrid.components import ComponentId

from ..electrical_component._state_snapshot import ElectricalComponentStateSnapshot
from ..metrics._sample import Metric, MetricSample, MetricSample2
from ._state_sample import ComponentStateSample


@dataclass(frozen=True, kw_only=True)
class ComponentDataSamples:
    """An aggregate of multiple metrics, states, and errors of a component."""

    component_id: ComponentId
    """The unique identifier of the component."""

    metric_samples: list[MetricSample]
    """The metrics sampled from the component."""

    states: list[ComponentStateSample]
    """The states sampled from the component."""


@dataclass(frozen=True, kw_only=True)
class ElectricalComponentTelemetry:
    """An aggregate of multiple metrics, operational states, and errors for a component."""

    electrical_component_id: ComponentId
    """The unique identifier of the component."""

    sample_time: datetime
    """The time when the samples were taken."""

    metric_samples: Mapping[Metric | int, MetricSample2 | Mapping[str, MetricSample2]]
    """The metrics sampled from the component.

    The keys are either `Metric` enum values or metric IDs (integers) if the value is
    not yet supported by the client.

    The value can be either a `MetricSample2` if the metric has no connection
    information, or a mapping from connection names identifying the connection to the
    `MetricSample2` for that particular connection.
    """

    state: ElectricalComponentStateSnapshot | None
    """The states sampled from the component."""
