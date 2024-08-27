# License: MIT
# Copyright © 2022 Frequenz Energy-as-a-Service GmbH

"""Tests for the microgrid client thin wrapper."""

import logging
from collections.abc import AsyncIterator
from contextlib import AsyncExitStack
from typing import Any
from unittest import mock

import grpc.aio
import pytest

# pylint: disable=no-name-in-module
from frequenz.api.common.components_pb2 import ComponentCategory as PbComponentCategory
from frequenz.api.common.components_pb2 import InverterType as PbInverterType
from frequenz.api.common.metrics_pb2 import Bounds as PbBounds
from frequenz.api.microgrid.grid_pb2 import Metadata as PbGridMetadata
from frequenz.api.microgrid.inverter_pb2 import Metadata as PbInverterMetadata
from frequenz.api.microgrid.microgrid_pb2 import Component as PbComponent
from frequenz.api.microgrid.microgrid_pb2 import ComponentData as PbComponentData
from frequenz.api.microgrid.microgrid_pb2 import ComponentList as PbComponentList
from frequenz.api.microgrid.microgrid_pb2 import Connection as PbConnection
from frequenz.api.microgrid.microgrid_pb2 import ConnectionFilter as PbConnectionFilter
from frequenz.api.microgrid.microgrid_pb2 import ConnectionList as PbConnectionList
from frequenz.api.microgrid.microgrid_pb2 import SetBoundsParam as PbSetBoundsParam
from frequenz.api.microgrid.microgrid_pb2 import (
    SetPowerActiveParam as PbSetPowerActiveParam,
)

# pylint: enable=no-name-in-module
from frequenz.client.base import retry

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


class _TestClient(ApiClient):
    def __init__(self, *, retry_strategy: retry.Strategy | None = None) -> None:
        # Here we sadly can't use spec=MicrogridStub because the generated stub typing
        # is a mess, and for some reason inspection of gRPC methods doesn't work.
        # This is also why we need to explicitly create the AsyncMock objects for every
        # call.
        mock_stub = mock.MagicMock(name="stub")
        mock_stub.ListComponents = mock.AsyncMock("ListComponents")
        mock_stub.ListConnections = mock.AsyncMock("ListConnections")
        mock_stub.SetPowerActive = mock.AsyncMock("SetPowerActive")
        mock_stub.AddInclusionBounds = mock.AsyncMock("AddInclusionBounds")
        mock_stub.StreamComponentData = mock.Mock("StreamComponentData")
        super().__init__("grpc://mock_host:1234", retry_strategy=retry_strategy)
        self.mock_stub = mock_stub
        self.api = mock_stub


async def test_components() -> None:
    """Test the components() method."""
    client = _TestClient()
    server_response = PbComponentList()
    client.mock_stub.ListComponents.return_value = server_response
    assert set(await client.components()) == set()

    server_response.components.append(
        PbComponent(id=0, category=PbComponentCategory.COMPONENT_CATEGORY_METER)
    )
    assert set(await client.components()) == {Component(0, ComponentCategory.METER)}

    server_response.components.append(
        PbComponent(id=0, category=PbComponentCategory.COMPONENT_CATEGORY_BATTERY)
    )
    assert set(await client.components()) == {
        Component(0, ComponentCategory.METER),
        Component(0, ComponentCategory.BATTERY),
    }

    server_response.components.append(
        PbComponent(id=0, category=PbComponentCategory.COMPONENT_CATEGORY_METER)
    )
    assert set(await client.components()) == {
        Component(0, ComponentCategory.METER),
        Component(0, ComponentCategory.BATTERY),
        Component(0, ComponentCategory.METER),
    }

    # sensors are not counted as components by the API client
    server_response.components.append(
        PbComponent(id=1, category=PbComponentCategory.COMPONENT_CATEGORY_SENSOR)
    )
    assert set(await client.components()) == {
        Component(0, ComponentCategory.METER),
        Component(0, ComponentCategory.BATTERY),
        Component(0, ComponentCategory.METER),
    }

    _replace_components(
        server_response,
        [
            PbComponent(id=9, category=PbComponentCategory.COMPONENT_CATEGORY_METER),
            PbComponent(
                id=99, category=PbComponentCategory.COMPONENT_CATEGORY_INVERTER
            ),
            PbComponent(id=666, category=PbComponentCategory.COMPONENT_CATEGORY_SENSOR),
            PbComponent(
                id=999, category=PbComponentCategory.COMPONENT_CATEGORY_BATTERY
            ),
        ],
    )
    assert set(await client.components()) == {
        Component(9, ComponentCategory.METER),
        Component(99, ComponentCategory.INVERTER, InverterType.NONE),
        Component(999, ComponentCategory.BATTERY),
    }

    _replace_components(
        server_response,
        [
            PbComponent(id=99, category=PbComponentCategory.COMPONENT_CATEGORY_SENSOR),
            PbComponent(
                id=100,
                category=PbComponentCategory.COMPONENT_CATEGORY_UNSPECIFIED,
            ),
            PbComponent(id=104, category=PbComponentCategory.COMPONENT_CATEGORY_METER),
            PbComponent(
                id=105,
                category=PbComponentCategory.COMPONENT_CATEGORY_INVERTER,
            ),
            PbComponent(
                id=106, category=PbComponentCategory.COMPONENT_CATEGORY_BATTERY
            ),
            PbComponent(
                id=107,
                category=PbComponentCategory.COMPONENT_CATEGORY_EV_CHARGER,
            ),
            PbComponent(id=999, category=PbComponentCategory.COMPONENT_CATEGORY_SENSOR),
            PbComponent(
                id=101,
                category=PbComponentCategory.COMPONENT_CATEGORY_GRID,
                grid=PbGridMetadata(rated_fuse_current=int(123.0)),
            ),
        ],
    )

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

    _replace_components(
        server_response,
        [
            PbComponent(id=9, category=PbComponentCategory.COMPONENT_CATEGORY_METER),
            PbComponent(id=666, category=PbComponentCategory.COMPONENT_CATEGORY_SENSOR),
            PbComponent(
                id=999, category=PbComponentCategory.COMPONENT_CATEGORY_BATTERY
            ),
            PbComponent(
                id=99,
                category=PbComponentCategory.COMPONENT_CATEGORY_INVERTER,
                inverter=PbInverterMetadata(type=PbInverterType.INVERTER_TYPE_BATTERY),
            ),
        ],
    )

    assert set(await client.components()) == {
        Component(9, ComponentCategory.METER),
        Component(99, ComponentCategory.INVERTER, InverterType.BATTERY),
        Component(999, ComponentCategory.BATTERY),
    }


async def test_components_grpc_error() -> None:
    """Test the components() method when the gRPC call fails."""
    client = _TestClient()
    client.mock_stub.ListComponents.side_effect = grpc.aio.AioRpcError(
        mock.MagicMock(name="mock_status"),
        mock.MagicMock(name="mock_initial_metadata"),
        mock.MagicMock(name="mock_trailing_metadata"),
        "fake grpc details",
        "fake grpc debug_error_string",
    )
    with pytest.raises(
        ClientError,
        match=r"Failed calling 'ListComponents' on 'grpc://mock_host:1234': .* "
        r"<status=<MagicMock name='mock_status\.name' id='.*'>>: fake grpc details "
        r"\(fake grpc debug_error_string\)",
    ):
        await client.components()


async def test_connections() -> None:
    """Test the connections() method."""
    client = _TestClient()

    def assert_filter(*, starts: set[int], ends: set[int]) -> None:
        client.mock_stub.ListConnections.assert_called_once()
        filter_ = client.mock_stub.ListConnections.call_args[0][0]
        assert isinstance(filter_, PbConnectionFilter)
        assert set(filter_.starts) == starts
        assert set(filter_.ends) == ends

    components_response = PbComponentList()
    connections_response = PbConnectionList()
    client.mock_stub.ListComponents.return_value = components_response
    client.mock_stub.ListConnections.return_value = connections_response
    assert set(await client.connections()) == set()
    assert_filter(starts=set(), ends=set())

    connections_response.connections.append(PbConnection(start=0, end=0))
    assert set(await client.connections()) == {Connection(0, 0)}

    components_response.components.extend(
        [
            PbComponent(id=7, category=PbComponentCategory.COMPONENT_CATEGORY_BATTERY),
            PbComponent(id=9, category=PbComponentCategory.COMPONENT_CATEGORY_INVERTER),
        ]
    )
    connections_response.connections.append(PbConnection(start=7, end=9))
    assert set(await client.connections()) == {
        Connection(0, 0),
        Connection(7, 9),
    }

    connections_response.connections.append(PbConnection(start=0, end=0))
    assert set(await client.connections()) == {
        Connection(0, 0),
        Connection(7, 9),
        Connection(0, 0),
    }

    _replace_connections(
        connections_response,
        [
            PbConnection(start=999, end=9),
            PbConnection(start=99, end=19),
            PbConnection(start=909, end=101),
            PbConnection(start=99, end=91),
        ],
    )
    for component_id in [999, 99, 19, 909, 101, 91]:
        components_response.components.append(
            PbComponent(
                id=component_id,
                category=PbComponentCategory.COMPONENT_CATEGORY_BATTERY,
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
            PbComponent(
                id=component_id,
                category=PbComponentCategory.COMPONENT_CATEGORY_BATTERY,
            )
        )
    _replace_connections(
        connections_response,
        [
            PbConnection(start=1, end=2),
            PbConnection(start=2, end=3),
            PbConnection(start=2, end=4),
            PbConnection(start=2, end=5),
            PbConnection(start=4, end=3),
            PbConnection(start=4, end=5),
            PbConnection(start=4, end=6),
            PbConnection(start=5, end=4),
            PbConnection(start=5, end=7),
            PbConnection(start=5, end=8),
        ],
    )
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
    client.mock_stub.ListConnections.side_effect = grpc.aio.AioRpcError(
        mock.MagicMock(name="mock_status"),
        mock.MagicMock(name="mock_initial_metadata"),
        mock.MagicMock(name="mock_trailing_metadata"),
        "fake grpc details",
        "fake grpc debug_error_string",
    )
    with pytest.raises(
        ClientError,
        match=r"Failed calling 'ListConnections' on 'grpc://mock_host:1234': .* "
        r"<status=<MagicMock name='mock_status\.name' id='.*'>>: fake grpc details "
        r"\(fake grpc debug_error_string\)",
    ):
        await client.connections()


@pytest.fixture
def meter83() -> PbComponent:
    """Return a test meter component."""
    return PbComponent(id=83, category=PbComponentCategory.COMPONENT_CATEGORY_METER)


@pytest.fixture
def battery38() -> PbComponent:
    """Return a test battery component."""
    return PbComponent(id=38, category=PbComponentCategory.COMPONENT_CATEGORY_BATTERY)


@pytest.fixture
def inverter99() -> PbComponent:
    """Return a test inverter component."""
    return PbComponent(id=99, category=PbComponentCategory.COMPONENT_CATEGORY_INVERTER)


@pytest.fixture
def ev_charger101() -> PbComponent:
    """Return a test EV charger component."""
    return PbComponent(
        id=101, category=PbComponentCategory.COMPONENT_CATEGORY_EV_CHARGER
    )


@pytest.fixture
def component_list(
    meter83: PbComponent,
    battery38: PbComponent,
    inverter99: PbComponent,
    ev_charger101: PbComponent,
) -> list[PbComponent]:
    """Return a list of test components."""
    return [meter83, battery38, inverter99, ev_charger101]


@pytest.mark.parametrize("method", ["meter_data", "battery_data", "inverter_data"])
async def test_data_component_not_found(method: str) -> None:
    """Test the meter_data() method."""
    client = _TestClient()
    client.mock_stub.ListComponents.return_value = PbComponentList()

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
    method: str, component_id: int, component_list: list[PbComponent]
) -> None:
    """Test the meter_data() method."""
    client = _TestClient()
    client.mock_stub.ListComponents.return_value = PbComponentList(
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
    component_list: list[PbComponent],
) -> None:
    """Test the meter_data() method."""
    client = _TestClient()
    client.mock_stub.ListComponents.return_value = PbComponentList(
        components=component_list
    )

    async def stream_data(
        *args: Any, **kwargs: Any  # pylint: disable=unused-argument
    ) -> AsyncIterator[PbComponentData]:
        yield PbComponentData(id=component_id)

    client.mock_stub.StreamComponentData.side_effect = stream_data
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
    component_list: list[PbComponent],
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test the components() method when the gRPC call fails."""
    caplog.set_level(logging.WARNING)
    client = _TestClient(
        retry_strategy=retry.LinearBackoff(interval=0.0, jitter=0.0, limit=6)
    )
    client.mock_stub.ListComponents.return_value = PbComponentList(
        components=component_list
    )

    num_calls = 0

    async def stream_data(
        *args: Any, **kwargs: Any  # pylint: disable=unused-argument
    ) -> AsyncIterator[PbComponentData]:
        nonlocal num_calls
        num_calls += 1
        if num_calls % 2:
            raise grpc.aio.AioRpcError(
                mock.MagicMock(name="mock_status"),
                mock.MagicMock(name="mock_initial_metadata"),
                mock.MagicMock(name="mock_trailing_metadata"),
                f"fake grpc details num_calls={num_calls}",
                "fake grpc debug_error_string",
            )
        yield PbComponentData(id=component_id)

    client.mock_stub.StreamComponentData.side_effect = stream_data
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
            assert f"fake grpc details num_calls={n+1}" in log_tuple[2]


@pytest.mark.parametrize("power_w", [0, 0.0, 12, -75, 0.1, -0.0001, 134.0])
async def test_set_power_ok(power_w: float, meter83: PbComponent) -> None:
    """Test if charge is able to charge component."""
    client = _TestClient()
    client.mock_stub.ListComponents.return_value = PbComponentList(components=[meter83])

    await client.set_power(component_id=83, power_w=power_w)
    client.mock_stub.SetPowerActive.assert_called_once()
    call_args = client.mock_stub.SetPowerActive.call_args[0]
    assert call_args[0] == PbSetPowerActiveParam(component_id=83, power=power_w)


async def test_set_power_grpc_error() -> None:
    """Test set_power() raises ClientError when the gRPC call fails."""
    client = _TestClient()
    client.mock_stub.SetPowerActive.side_effect = grpc.aio.AioRpcError(
        mock.MagicMock(name="mock_status"),
        mock.MagicMock(name="mock_initial_metadata"),
        mock.MagicMock(name="mock_trailing_metadata"),
        "fake grpc details",
        "fake grpc debug_error_string",
    )
    with pytest.raises(
        ClientError,
        match=r"Failed calling 'SetPowerActive' on 'grpc://mock_host:1234': .* "
        r"<status=<MagicMock name='mock_status\.name' id='.*'>>: fake grpc details "
        r"\(fake grpc debug_error_string\)",
    ):
        await client.set_power(component_id=83, power_w=100.0)


@pytest.mark.parametrize(
    "bounds",
    [
        PbBounds(lower=0.0, upper=0.0),
        PbBounds(lower=0.0, upper=2.0),
        PbBounds(lower=-10.0, upper=0.0),
        PbBounds(lower=-10.0, upper=2.0),
    ],
    ids=str,
)
async def test_set_bounds_ok(bounds: PbBounds, inverter99: PbComponent) -> None:
    """Test if charge is able to charge component."""
    client = _TestClient()
    client.mock_stub.ListComponents.return_value = PbComponentList(
        components=[inverter99]
    )

    await client.set_bounds(99, bounds.lower, bounds.upper)
    client.mock_stub.AddInclusionBounds.assert_called_once()
    call_args = client.mock_stub.AddInclusionBounds.call_args[0]
    assert call_args[0] == PbSetBoundsParam(
        component_id=99,
        target_metric=PbSetBoundsParam.TargetMetric.TARGET_METRIC_POWER_ACTIVE,
        bounds=bounds,
    )


@pytest.mark.parametrize(
    "bounds",
    [
        PbBounds(lower=0.0, upper=-2.0),
        PbBounds(lower=10.0, upper=-2.0),
        PbBounds(lower=10.0, upper=0.0),
    ],
    ids=str,
)
async def test_set_bounds_fail(bounds: PbBounds, inverter99: PbComponent) -> None:
    """Test if charge is able to charge component."""
    client = _TestClient()
    client.mock_stub.ListComponents.return_value = PbComponentList(
        components=[inverter99]
    )

    with pytest.raises(ValueError):
        await client.set_bounds(99, bounds.lower, bounds.upper)
    client.mock_stub.AddInclusionBounds.assert_not_called()


async def test_set_bounds_grpc_error() -> None:
    """Test the components() method when the gRPC call fails."""
    client = _TestClient()
    client.mock_stub.AddInclusionBounds.side_effect = grpc.aio.AioRpcError(
        mock.MagicMock(name="mock_status"),
        mock.MagicMock(name="mock_initial_metadata"),
        mock.MagicMock(name="mock_trailing_metadata"),
        "fake grpc details",
        "fake grpc debug_error_string",
    )
    with pytest.raises(
        ClientError,
        match=r"Failed calling 'AddInclusionBounds' on 'grpc://mock_host:1234': .* "
        r"<status=<MagicMock name='mock_status\.name' id='.*'>>: fake grpc details "
        r"\(fake grpc debug_error_string\)",
    ):
        await client.set_bounds(99, 0.0, 100.0)


def _clear_components(component_list: PbComponentList) -> None:
    while component_list.components:
        component_list.components.pop()


def _replace_components(
    component_list: PbComponentList, components: list[PbComponent]
) -> None:
    _clear_components(component_list)
    component_list.components.extend(components)


def _clear_connections(connection_list: PbConnectionList) -> None:
    while connection_list.connections:
        connection_list.connections.pop()


def _replace_connections(
    connection_list: PbConnectionList, connections: list[PbConnection]
) -> None:
    _clear_connections(connection_list)
    connection_list.connections.extend(connections)
