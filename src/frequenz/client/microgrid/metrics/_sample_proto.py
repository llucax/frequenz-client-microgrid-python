# License: MIT
# Copyright © 2024 Frequenz Energy-as-a-Service GmbH

"""Loading of MetricSample and AggregatedMetricValue objects from protobuf messages."""

from frequenz.api.common.v1.metrics import metric_sample_pb2
from frequenz.client.base import conversion

from frequenz.client.microgrid.metrics._bounds_proto import bounds_from_proto

from .._util import enum_from_proto
from ..metrics._metric import Metric
from ._sample import AggregatedMetricValue, MetricSample


def aggregated_metric_sample_from_proto(
    message: metric_sample_pb2.AggregatedMetricValue,
) -> AggregatedMetricValue:
    """Convert a protobuf message to a `AggregatedMetricValue` object.

    Args:
        message: The protobuf message to convert.

    Returns:
        The resulting `AggregatedMetricValue` object.
    """
    return AggregatedMetricValue(
        avg=message.avg_value,
        min=message.min_value,
        max=message.max_value,
        raw_values=message.raw_values,
    )


def metric_sample_from_proto(
    message: metric_sample_pb2.MetricSample,
) -> MetricSample:
    """Convert a protobuf message to a `MetricSample` object.

    Args:
        message: The protobuf message to convert.

    Returns:
        The resulting `MetricSample` object.
    """
    value: float | AggregatedMetricValue | None = None
    if message.HasField("value"):
        match message.value.WhichOneof("metric_value_variant"):
            case "simple_metric":
                value = message.value.simple_metric.value
            case "aggregated_metric":
                value = aggregated_metric_sample_from_proto(
                    message.value.aggregated_metric
                )

    return MetricSample(
        sampled_at=conversion.to_datetime(message.sampled_at),
        metric=enum_from_proto(message.metric, Metric),
        value=value,
        bounds=[bounds_from_proto(b) for b in message.bounds],
        connection=message.source,
    )
