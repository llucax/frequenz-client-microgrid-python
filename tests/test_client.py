# License: MIT
# Copyright © 2022 Frequenz Energy-as-a-Service GmbH

"""Tests for the microgrid client thin wrapper."""

import logging
from collections.abc import AsyncIterator
from contextlib import AsyncExitStack
from typing import Any
from unittest import mock

import grpclib
import grpclib.client
import pytest
from frequenz.client.base import retry
from frequenz.microgrid.betterproto.frequenz.api import microgrid
from frequenz.microgrid.betterproto.frequenz.api.common import components, metrics
from frequenz.microgrid.betterproto.frequenz.api.microgrid import grid, inverter

from frequenz.client.microgrid import (
    ApiClient,
    BatteryData,
    ClientError,
    Component,
    ComponentCategory,
    ComponentData,
    EVChargerData,
    Fuse,
    GridMetadata,
    InverterData,
    InverterType,
    MeterData,
)
from frequenz.client.microgrid._connection import Connection

# @contextlib.asynccontextmanager
# async def _gprc_server(
#     servicer: mock_api.MockMicrogridServicer | None = None,
# ) -> AsyncIterator[tuple[mock_api.MockMicrogridServicer, ApiClient]]:
#     global _CURRENT_PORT  # pylint: disable=global-statement
#     port = _CURRENT_PORT
#     _CURRENT_PORT += 1
#     if servicer is None:
#         servicer = mock_api.MockMicrogridServicer()
#     server = mock_api.MockGrpcServer(servicer, port=port)
#     client = ApiClient(
#         grpc.aio.insecure_channel(f"[::]:{port}"),
#         f"[::]:{port}",
#         retry_strategy=LinearBackoff(interval=0.0, jitter=0.05),
#     )
#     await server.start()
#     try:
#         yield servicer, client
#     finally:
#         assert await server.graceful_shutdown()


class _TestClient(ApiClient):
    def __init__(self, *, retry_strategy: retry.Strategy | None = None) -> None:
        mock_stub = mock.MagicMock(name="stub", spec=microgrid.MicrogridStub)
        super().__init__("grpc://mock_host:1234", retry_strategy=retry_strategy)
        self.mock_stub = mock_stub
        self.api = mock_stub


async def test_components() -> None:
    """Test the components() method."""
    client = _TestClient()
    server_response = microgrid.ComponentList()
    client.mock_stub.list_components.return_value = server_response
    assert set(await client.components()) == set()

    server_response.components.append(
        microgrid.Component(
            id=0, category=components.ComponentCategory.COMPONENT_CATEGORY_METER
        )
    )
    assert set(await client.components()) == {Component(0, ComponentCategory.METER)}

    server_response.components.append(
        microgrid.Component(
            id=0, category=components.ComponentCategory.COMPONENT_CATEGORY_BATTERY
        )
    )
    assert set(await client.components()) == {
        Component(0, ComponentCategory.METER),
        Component(0, ComponentCategory.BATTERY),
    }

    server_response.components.append(
        microgrid.Component(
            id=0, category=components.ComponentCategory.COMPONENT_CATEGORY_METER
        )
    )
    assert set(await client.components()) == {
        Component(0, ComponentCategory.METER),
        Component(0, ComponentCategory.BATTERY),
        Component(0, ComponentCategory.METER),
    }

    # sensors are not counted as components by the API client
    server_response.components.append(
        microgrid.Component(
            id=1, category=components.ComponentCategory.COMPONENT_CATEGORY_SENSOR
        )
    )
    assert set(await client.components()) == {
        Component(0, ComponentCategory.METER),
        Component(0, ComponentCategory.BATTERY),
        Component(0, ComponentCategory.METER),
    }

    server_response.components[:] = [
        microgrid.Component(
            id=9, category=components.ComponentCategory.COMPONENT_CATEGORY_METER
        ),
        microgrid.Component(
            id=99, category=components.ComponentCategory.COMPONENT_CATEGORY_INVERTER
        ),
        microgrid.Component(
            id=666, category=components.ComponentCategory.COMPONENT_CATEGORY_SENSOR
        ),
        microgrid.Component(
            id=999, category=components.ComponentCategory.COMPONENT_CATEGORY_BATTERY
        ),
    ]
    assert set(await client.components()) == {
        Component(9, ComponentCategory.METER),
        Component(99, ComponentCategory.INVERTER, InverterType.NONE),
        Component(999, ComponentCategory.BATTERY),
    }

    server_response.components[:] = [
        microgrid.Component(
            id=99, category=components.ComponentCategory.COMPONENT_CATEGORY_SENSOR
        ),
        microgrid.Component(
            id=100,
            category=components.ComponentCategory.COMPONENT_CATEGORY_UNSPECIFIED,
        ),
        microgrid.Component(
            id=104, category=components.ComponentCategory.COMPONENT_CATEGORY_METER
        ),
        microgrid.Component(
            id=105,
            category=components.ComponentCategory.COMPONENT_CATEGORY_INVERTER,
        ),
        microgrid.Component(
            id=106, category=components.ComponentCategory.COMPONENT_CATEGORY_BATTERY
        ),
        microgrid.Component(
            id=107,
            category=components.ComponentCategory.COMPONENT_CATEGORY_EV_CHARGER,
        ),
        microgrid.Component(
            id=999, category=components.ComponentCategory.COMPONENT_CATEGORY_SENSOR
        ),
        microgrid.Component(
            id=101,
            category=components.ComponentCategory.COMPONENT_CATEGORY_GRID,
            grid=grid.Metadata(rated_fuse_current=int(123.0)),
        ),
    ]

    grid_fuse = Fuse(123.0)

    assert set(await client.components()) == {
        Component(100, ComponentCategory.NONE),
        Component(
            101,
            ComponentCategory.GRID,
            None,
            GridMetadata(fuse=grid_fuse),
        ),
        Component(104, ComponentCategory.METER),
        Component(105, ComponentCategory.INVERTER, InverterType.NONE),
        Component(106, ComponentCategory.BATTERY),
        Component(107, ComponentCategory.EV_CHARGER),
    }

    server_response.components[:] = [
        microgrid.Component(
            id=9, category=components.ComponentCategory.COMPONENT_CATEGORY_METER
        ),
        microgrid.Component(
            id=666, category=components.ComponentCategory.COMPONENT_CATEGORY_SENSOR
        ),
        microgrid.Component(
            id=999, category=components.ComponentCategory.COMPONENT_CATEGORY_BATTERY
        ),
        microgrid.Component(
            id=99,
            category=components.ComponentCategory.COMPONENT_CATEGORY_INVERTER,
            inverter=inverter.Metadata(
                type=components.InverterType.INVERTER_TYPE_BATTERY
            ),
        ),
    ]

    assert set(await client.components()) == {
        Component(9, ComponentCategory.METER),
        Component(99, ComponentCategory.INVERTER, InverterType.BATTERY),
        Component(999, ComponentCategory.BATTERY),
    }


async def test_components_grpc_error() -> None:
    """Test the components() method when the gRPC call fails."""
    client = _TestClient()
    client.mock_stub.list_components.side_effect = grpclib.GRPCError(
        mock.MagicMock(name="mock status"), "fake grpc error"
    )
    with pytest.raises(
        ClientError,
        match="Failed to list components. Microgrid API: grpc://mock_host:1234. "
        "Err: .*fake grpc error",
    ):
        await client.components()


async def test_connections() -> None:
    """Test the connections() method."""
    client = _TestClient()

    def assert_filter(*, starts: set[int], ends: set[int]) -> None:
        client.mock_stub.list_connections.assert_called_once()
        filter_ = client.mock_stub.list_connections.call_args[0][0]
        assert isinstance(filter_, microgrid.ConnectionFilter)
        assert set(filter_.starts) == starts
        assert set(filter_.ends) == ends

    components_response = microgrid.ComponentList()
    connections_response = microgrid.ConnectionList()
    client.mock_stub.list_components.return_value = components_response
    client.mock_stub.list_connections.return_value = connections_response
    assert set(await client.connections()) == set()
    assert_filter(starts=set(), ends=set())

    connections_response.connections.append(microgrid.Connection(start=0, end=0))
    assert set(await client.connections()) == {Connection(0, 0)}

    components_response.components.extend(
        [
            microgrid.Component(
                id=7, category=components.ComponentCategory.COMPONENT_CATEGORY_BATTERY
            ),
            microgrid.Component(
                id=9, category=components.ComponentCategory.COMPONENT_CATEGORY_INVERTER
            ),
        ]
    )
    connections_response.connections.append(microgrid.Connection(start=7, end=9))
    assert set(await client.connections()) == {
        Connection(0, 0),
        Connection(7, 9),
    }

    connections_response.connections.append(microgrid.Connection(start=0, end=0))
    assert set(await client.connections()) == {
        Connection(0, 0),
        Connection(7, 9),
        Connection(0, 0),
    }

    connections_response.connections[:] = [
        microgrid.Connection(start=999, end=9),
        microgrid.Connection(start=99, end=19),
        microgrid.Connection(start=909, end=101),
        microgrid.Connection(start=99, end=91),
    ]
    for component_id in [999, 99, 19, 909, 101, 91]:
        components_response.components.append(
            microgrid.Component(
                id=component_id,
                category=components.ComponentCategory.COMPONENT_CATEGORY_BATTERY,
            )
        )
    assert set(await client.connections()) == {
        Connection(999, 9),
        Connection(99, 19),
        Connection(909, 101),
        Connection(99, 91),
    }

    for component_id in [1, 2, 3, 4, 5, 6, 7, 8]:
        components_response.components.append(
            microgrid.Component(
                id=component_id,
                category=components.ComponentCategory.COMPONENT_CATEGORY_BATTERY,
            )
        )
    connections_response.connections[:] = [
        microgrid.Connection(start=1, end=2),
        microgrid.Connection(start=2, end=3),
        microgrid.Connection(start=2, end=4),
        microgrid.Connection(start=2, end=5),
        microgrid.Connection(start=4, end=3),
        microgrid.Connection(start=4, end=5),
        microgrid.Connection(start=4, end=6),
        microgrid.Connection(start=5, end=4),
        microgrid.Connection(start=5, end=7),
        microgrid.Connection(start=5, end=8),
    ]
    assert set(await client.connections()) == {
        Connection(1, 2),
        Connection(2, 3),
        Connection(2, 4),
        Connection(2, 5),
        Connection(4, 3),
        Connection(4, 5),
        Connection(4, 6),
        Connection(5, 4),
        Connection(5, 7),
        Connection(5, 8),
    }

    # passing empty sets is the same as passing `None`,
    # filter is ignored
    client.mock_stub.reset_mock()
    await client.connections(starts=set(), ends=set())
    assert_filter(starts=set(), ends=set())

    # include filter for connection start
    client.mock_stub.reset_mock()
    await client.connections(starts={1, 2})
    assert_filter(starts={1, 2}, ends=set())

    client.mock_stub.reset_mock()
    await client.connections(starts={2})
    assert_filter(starts={2}, ends=set())

    # include filter for connection end
    client.mock_stub.reset_mock()
    await client.connections(ends={1})
    assert_filter(starts=set(), ends={1})

    client.mock_stub.reset_mock()
    await client.connections(ends={2, 4, 5})
    assert_filter(starts=set(), ends={2, 4, 5})

    # different filters combine with AND logic
    client.mock_stub.reset_mock()
    await client.connections(starts={1, 2, 4}, ends={4, 5, 6})
    assert_filter(starts={1, 2, 4}, ends={4, 5, 6})


async def test_connections_grpc_error() -> None:
    """Test the components() method when the gRPC call fails."""
    client = _TestClient()
    client.mock_stub.list_connections.side_effect = grpclib.GRPCError(
        mock.MagicMock(name="mock status"), "fake grpc error"
    )
    with pytest.raises(
        ClientError,
        match="Failed to list connections. Microgrid API: grpc://mock_host:1234. "
        "Err: .*fake grpc error",
    ):
        await client.connections()


@pytest.fixture
def meter83() -> microgrid.Component:
    """Return a test meter component."""
    return microgrid.Component(
        id=83, category=components.ComponentCategory.COMPONENT_CATEGORY_METER
    )


@pytest.fixture
def battery38() -> microgrid.Component:
    """Return a test battery component."""
    return microgrid.Component(
        id=38, category=components.ComponentCategory.COMPONENT_CATEGORY_BATTERY
    )


@pytest.fixture
def inverter99() -> microgrid.Component:
    """Return a test inverter component."""
    return microgrid.Component(
        id=99, category=components.ComponentCategory.COMPONENT_CATEGORY_INVERTER
    )


@pytest.fixture
def ev_charger101() -> microgrid.Component:
    """Return a test EV charger component."""
    return microgrid.Component(
        id=101, category=components.ComponentCategory.COMPONENT_CATEGORY_EV_CHARGER
    )


@pytest.fixture
def component_list(
    meter83: microgrid.Component,
    battery38: microgrid.Component,
    inverter99: microgrid.Component,
    ev_charger101: microgrid.Component,
) -> list[microgrid.Component]:
    """Return a list of test components."""
    return [meter83, battery38, inverter99, ev_charger101]


@pytest.mark.parametrize("method", ["meter_data", "battery_data", "inverter_data"])
async def test_data_component_not_found(method: str) -> None:
    """Test the meter_data() method."""
    client = _TestClient()
    client.mock_stub.list_components.return_value = microgrid.ComponentList()

    # It should raise a ValueError for a missing component_id
    with pytest.raises(ValueError, match="Unable to find component with id 20"):
        await getattr(client, method)(20)


@pytest.mark.parametrize(
    "method, component_id",
    [
        ("meter_data", 38),
        ("battery_data", 83),
        ("inverter_data", 83),
        ("ev_charger_data", 99),
    ],
)
async def test_data_bad_category(
    method: str, component_id: int, component_list: list[microgrid.Component]
) -> None:
    """Test the meter_data() method."""
    client = _TestClient()
    client.mock_stub.list_components.return_value = microgrid.ComponentList(
        components=component_list
    )

    # It should raise a ValueError for a wrong component category
    with pytest.raises(
        ValueError, match=f"Component id {component_id} is a .*, not a {method[:-5]}"
    ):
        await getattr(client, method)(component_id)


@pytest.mark.parametrize(
    "method, component_id, component_class",
    [
        ("meter_data", 83, MeterData),
        ("battery_data", 38, BatteryData),
        ("inverter_data", 99, InverterData),
        ("ev_charger_data", 101, EVChargerData),
    ],
)
async def test_component_data(
    method: str,
    component_id: int,
    component_class: type[ComponentData],
    component_list: list[microgrid.Component],
) -> None:
    """Test the meter_data() method."""
    client = _TestClient()
    client.mock_stub.list_components.return_value = microgrid.ComponentList(
        components=component_list
    )

    async def stream_data(
        *args: Any, **kwargs: Any  # pylint: disable=unused-argument
    ) -> AsyncIterator[microgrid.ComponentData]:
        yield microgrid.ComponentData(id=component_id)

    client.mock_stub.stream_component_data.side_effect = stream_data
    receiver = await getattr(client, method)(component_id)
    async with AsyncExitStack() as stack:
        stack.push_async_callback(
            client._broadcasters[component_id].stop  # pylint: disable=protected-access
        )
        latest = await receiver.receive()
        assert isinstance(latest, component_class)
        assert latest.component_id == component_id


@pytest.mark.parametrize(
    "method, component_id, component_class",
    [
        ("meter_data", 83, MeterData),
        ("battery_data", 38, BatteryData),
        ("inverter_data", 99, InverterData),
        ("ev_charger_data", 101, EVChargerData),
    ],
)
async def test_component_data_grpc_error(
    method: str,
    component_id: int,
    component_class: type[ComponentData],
    component_list: list[microgrid.Component],
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test the components() method when the gRPC call fails."""
    caplog.set_level(logging.WARNING)
    client = _TestClient(
        retry_strategy=retry.LinearBackoff(interval=0.0, jitter=0.0, limit=6)
    )
    client.mock_stub.list_components.return_value = microgrid.ComponentList(
        components=component_list
    )

    num_calls = 0

    async def stream_data(
        *args: Any, **kwargs: Any  # pylint: disable=unused-argument
    ) -> AsyncIterator[microgrid.ComponentData]:
        nonlocal num_calls
        num_calls += 1
        if num_calls % 2:
            raise grpclib.GRPCError(
                mock.MagicMock(name="mock status"), f"fake grpc error {num_calls}"
            )
        yield microgrid.ComponentData(id=component_id)

    client.mock_stub.stream_component_data.side_effect = stream_data
    receiver = await getattr(client, method)(component_id)
    async with AsyncExitStack() as stack:
        stack.push_async_callback(
            client._broadcasters[component_id].stop  # pylint: disable=protected-access
        )
        latest = await receiver.receive()
        assert isinstance(latest, component_class)
        assert latest.component_id == component_id

        latest = await receiver.receive()
        assert isinstance(latest, component_class)
        assert latest.component_id == component_id

        latest = await receiver.receive()
        assert isinstance(latest, component_class)
        assert latest.component_id == component_id

    # This is not super portable, it will change if the GrpcStreamBroadcaster changes,
    # but without this there isn't much to check by this test.
    assert len(caplog.record_tuples) == 6
    for n, log_tuple in enumerate(caplog.record_tuples):
        assert log_tuple[0] == "frequenz.client.base.streaming"
        assert log_tuple[1] == logging.WARNING
        assert (
            f"raw-component-data-{component_id}: connection ended, retrying"
            in log_tuple[2]
        )
        if n % 2:
            assert "Stream exhausted" in log_tuple[2]
        else:
            assert f"fake grpc error {n+1}" in log_tuple[2]


@pytest.mark.parametrize("power_w", [0, 0.0, 12, -75, 0.1, -0.0001, 134.0])
async def test_set_power_ok(power_w: float, meter83: microgrid.Component) -> None:
    """Test if charge is able to charge component."""
    client = _TestClient()
    client.mock_stub.list_components.return_value = microgrid.ComponentList(
        components=[meter83]
    )

    await client.set_power(component_id=83, power_w=power_w)
    client.mock_stub.set_power_active.assert_called_once()
    call_args = client.mock_stub.set_power_active.call_args[0]
    assert call_args[0] == microgrid.SetPowerActiveParam(component_id=83, power=power_w)


async def test_set_power_grpc_error() -> None:
    """Test set_power() raises ClientError when the gRPC call fails."""
    client = _TestClient()
    client.mock_stub.set_power_active.side_effect = grpclib.GRPCError(
        mock.MagicMock(name="mock status"), "fake grpc error"
    )
    with pytest.raises(
        ClientError,
        match="Failed to set power. Microgrid API: grpc://mock_host:1234. "
        "Err: .*fake grpc error",
    ):
        await client.set_power(component_id=83, power_w=100.0)


@pytest.mark.parametrize(
    "bounds",
    [
        metrics.Bounds(lower=0.0, upper=0.0),
        metrics.Bounds(lower=0.0, upper=2.0),
        metrics.Bounds(lower=-10.0, upper=0.0),
        metrics.Bounds(lower=-10.0, upper=2.0),
    ],
    ids=str,
)
async def test_set_bounds_ok(
    bounds: metrics.Bounds, inverter99: microgrid.Component
) -> None:
    """Test if charge is able to charge component."""
    client = _TestClient()
    client.mock_stub.list_components.return_value = microgrid.ComponentList(
        components=[inverter99]
    )

    await client.set_bounds(99, bounds.lower, bounds.upper)
    client.mock_stub.add_inclusion_bounds.assert_called_once()
    call_args = client.mock_stub.add_inclusion_bounds.call_args[0]
    assert call_args[0] == microgrid.SetBoundsParam(
        component_id=99,
        target_metric=microgrid.SetBoundsParamTargetMetric.TARGET_METRIC_POWER_ACTIVE,
        bounds=bounds,
    )


@pytest.mark.parametrize(
    "bounds",
    [
        metrics.Bounds(lower=0.0, upper=-2.0),
        metrics.Bounds(lower=10.0, upper=-2.0),
        metrics.Bounds(lower=10.0, upper=0.0),
    ],
    ids=str,
)
async def test_set_bounds_fail(
    bounds: metrics.Bounds, inverter99: microgrid.Component
) -> None:
    """Test if charge is able to charge component."""
    client = _TestClient()
    client.mock_stub.list_components.return_value = microgrid.ComponentList(
        components=[inverter99]
    )

    with pytest.raises(ValueError):
        await client.set_bounds(99, bounds.lower, bounds.upper)
    client.mock_stub.add_inclusion_bounds.assert_not_called()


async def test_set_bounds_grpc_error() -> None:
    """Test the components() method when the gRPC call fails."""
    client = _TestClient()
    client.mock_stub.add_inclusion_bounds.side_effect = grpclib.GRPCError(
        mock.MagicMock(name="mock status"), "fake grpc error"
    )
    with pytest.raises(
        ClientError,
        match="Failed to set inclusion bounds. Microgrid API: grpc://mock_host:1234. "
        "Err: .*fake grpc error",
    ):
        await client.set_bounds(99, 0.0, 100.0)
