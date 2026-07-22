# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Test list_connections with mixed ElectricalComponentId and Component objects."""

from datetime import datetime, timezone
from typing import Any

from frequenz.api.microgrid.v1alpha18 import microgrid_pb2
from frequenz.client.common.microgrid import MicrogridId
from frequenz.client.common.microgrid.electrical_components import ElectricalComponentId

from frequenz.client.microgrid.component import GridConnectionPoint, Meter

# Mix ElectricalComponentId and Component objects
grid_component = GridConnectionPoint(
    id=ElectricalComponentId(1), microgrid_id=MicrogridId(1), rated_fuse_current=10_000
)
meter_component = Meter(id=ElectricalComponentId(4), microgrid_id=MicrogridId(1))

client_kwargs = {
    "sources": [grid_component, ElectricalComponentId(2)],
    "destinations": [ElectricalComponentId(3), meter_component],
}


def assert_stub_method_call(stub_method: Any) -> None:
    """Assert that the gRPC request matches the expected request."""
    stub_method.assert_called_once_with(
        microgrid_pb2.ListElectricalComponentConnectionsRequest(
            source_electrical_component_ids=[1, 2],
            destination_electrical_component_ids=[3, 4],
        ),
        timeout=60.0,
    )


lifetime_start = datetime(2023, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
grpc_response = microgrid_pb2.ListElectricalComponentConnectionsResponse(
    electrical_component_connections=[]
)


def assert_client_result(actual_result: Any) -> None:
    """Assert that the client result matches the expected connections list."""
    assert not list(actual_result)
