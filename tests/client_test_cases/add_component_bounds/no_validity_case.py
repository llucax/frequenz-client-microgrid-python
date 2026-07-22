# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Test data for add_component_bounds call without validity."""

from typing import Any

from frequenz.api.common.v1alpha8.metrics import bounds_pb2, metrics_pb2
from frequenz.api.microgrid.v1alpha18 import microgrid_pb2
from frequenz.client.common.microgrid.electrical_components import ElectricalComponentId

from frequenz.client.microgrid.metrics import Bounds, Metric

client_args = (
    ElectricalComponentId(1),
    Metric.AC_VOLTAGE,
    [Bounds(lower=200.0, upper=250.0)],
)


def assert_stub_method_call(stub_method: Any) -> None:
    """Assert that the gRPC request matches the expected request."""
    stub_method.assert_called_once_with(
        microgrid_pb2.AugmentElectricalComponentBoundsRequest(
            electrical_component_id=1,
            target_metric=metrics_pb2.Metric.METRIC_AC_VOLTAGE,
            bounds=[bounds_pb2.Bounds(lower=200.0, upper=250.0)],
            # No validity field
        ),
        timeout=60.0,
    )


grpc_response = microgrid_pb2.AugmentElectricalComponentBoundsResponse()


def assert_client_result(result: Any) -> None:
    """Assert that the client result is None as expected."""
    assert result is None
