# License: MIT
# Copyright © 2022 Frequenz Energy-as-a-Service GmbH

"""Tests for the microgrid client thin wrapper."""

import asyncio
import contextlib
from collections.abc import AsyncIterator

import grpc.aio
import pytest

# pylint: disable=no-name-in-module
from frequenz.api.common.components_pb2 import ComponentCategory as PbComponentCategory
from frequenz.api.common.components_pb2 import InverterType as PbInverterType
from frequenz.api.common.metrics_pb2 import Bounds as PbBounds
from frequenz.api.microgrid.microgrid_pb2 import ComponentList as PbComponentList
from frequenz.api.microgrid.microgrid_pb2 import ConnectionFilter as PbConnectionFilter
from frequenz.api.microgrid.microgrid_pb2 import ConnectionList as PbConnectionList
from frequenz.api.microgrid.microgrid_pb2 import SetBoundsParam as PbSetBoundsParam
from google.protobuf.empty_pb2 import Empty

# pylint: enable=no-name-in-module
from frequenz.client.microgrid import _client as client
from frequenz.client.microgrid._component import (
    Component,
    ComponentCategory,
    Fuse,
    GridMetadata,
    InverterType,
)
from frequenz.client.microgrid._component_data import (
    BatteryData,
    EVChargerData,
    InverterData,
    MeterData,
)
from frequenz.client.microgrid._connection import Connection
from frequenz.client.microgrid._retry import LinearBackoff

from . import mock_api

# pylint: disable=missing-function-docstring
# pylint: disable=missing-class-docstring


# This incrementing port is a hack to avoid the inherent flakiness of the approach of
# using a real GRPC (mock) server. The server seems to stay alive for a short time after
# the test is finished, which causes the next test to fail because the port is already
# in use.
# This is a workaround until we have a better solution.
# See https://github.com/frequenz-floss/frequenz-sdk-python/issues/662
_CURRENT_PORT: int = 57897


@contextlib.asynccontextmanager
async def _gprc_server(
    servicer: mock_api.MockMicrogridServicer | None = None,
) -> AsyncIterator[tuple[mock_api.MockMicrogridServicer, client.ApiClient]]:
    global _CURRENT_PORT  # pylint: disable=global-statement
    port = _CURRENT_PORT
    _CURRENT_PORT += 1
    if servicer is None:
        servicer = mock_api.MockMicrogridServicer()
    server = mock_api.MockGrpcServer(servicer, port=port)
    microgrid = client.ApiClient(
        grpc.aio.insecure_channel(f"[::]:{port}"),
        f"[::]:{port}",
        retry_spec=LinearBackoff(interval=0.0, jitter=0.05),
    )
    await server.start()
    try:
        yield servicer, microgrid
    finally:
        assert await server.graceful_shutdown()


class TestMicrogridGrpcClient:
    """Tests for the microgrid client thin wrapper."""

    async def test_components(self) -> None:
        """Test the components() method."""
        async with _gprc_server() as (servicer, microgrid):
            assert set(await microgrid.components()) == set()

            servicer.add_component(0, PbComponentCategory.COMPONENT_CATEGORY_METER)
            assert set(await microgrid.components()) == {
                Component(0, ComponentCategory.METER)
            }

            servicer.add_component(0, PbComponentCategory.COMPONENT_CATEGORY_BATTERY)
            assert set(await microgrid.components()) == {
                Component(0, ComponentCategory.METER),
                Component(0, ComponentCategory.BATTERY),
            }

            servicer.add_component(0, PbComponentCategory.COMPONENT_CATEGORY_METER)
            assert set(await microgrid.components()) == {
                Component(0, ComponentCategory.METER),
                Component(0, ComponentCategory.BATTERY),
                Component(0, ComponentCategory.METER),
            }

            # sensors are not counted as components by the API client
            servicer.add_component(1, PbComponentCategory.COMPONENT_CATEGORY_SENSOR)
            assert set(await microgrid.components()) == {
                Component(0, ComponentCategory.METER),
                Component(0, ComponentCategory.BATTERY),
                Component(0, ComponentCategory.METER),
            }

            servicer.set_components(
                [
                    (9, PbComponentCategory.COMPONENT_CATEGORY_METER),
                    (99, PbComponentCategory.COMPONENT_CATEGORY_INVERTER),
                    (666, PbComponentCategory.COMPONENT_CATEGORY_SENSOR),
                    (999, PbComponentCategory.COMPONENT_CATEGORY_BATTERY),
                ]
            )
            assert set(await microgrid.components()) == {
                Component(9, ComponentCategory.METER),
                Component(99, ComponentCategory.INVERTER, InverterType.NONE),
                Component(999, ComponentCategory.BATTERY),
            }

            servicer.set_components(
                [
                    (99, PbComponentCategory.COMPONENT_CATEGORY_SENSOR),
                    (
                        100,
                        PbComponentCategory.COMPONENT_CATEGORY_UNSPECIFIED,
                    ),
                    (104, PbComponentCategory.COMPONENT_CATEGORY_METER),
                    (105, PbComponentCategory.COMPONENT_CATEGORY_INVERTER),
                    (106, PbComponentCategory.COMPONENT_CATEGORY_BATTERY),
                    (
                        107,
                        PbComponentCategory.COMPONENT_CATEGORY_EV_CHARGER,
                    ),
                    (999, PbComponentCategory.COMPONENT_CATEGORY_SENSOR),
                ]
            )

            servicer.add_component(
                101,
                PbComponentCategory.COMPONENT_CATEGORY_GRID,
                123.0,
            )

            grid_max_current = 123.0
            grid_fuse = Fuse(grid_max_current)

            assert set(await microgrid.components()) == {
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

            servicer.set_components(
                [
                    (9, PbComponentCategory.COMPONENT_CATEGORY_METER),
                    (666, PbComponentCategory.COMPONENT_CATEGORY_SENSOR),
                    (999, PbComponentCategory.COMPONENT_CATEGORY_BATTERY),
                ]
            )
            servicer.add_component(
                99,
                PbComponentCategory.COMPONENT_CATEGORY_INVERTER,
                None,
                PbInverterType.INVERTER_TYPE_BATTERY,
            )

            assert set(await microgrid.components()) == {
                Component(9, ComponentCategory.METER),
                Component(99, ComponentCategory.INVERTER, InverterType.BATTERY),
                Component(999, ComponentCategory.BATTERY),
            }

    async def test_connections(self) -> None:
        """Test the connections() method."""
        async with _gprc_server() as (servicer, microgrid):
            assert set(await microgrid.connections()) == set()

            servicer.add_connection(0, 0)
            assert set(await microgrid.connections()) == {Connection(0, 0)}

            servicer.add_connection(7, 9)
            servicer.add_component(
                7,
                component_category=PbComponentCategory.COMPONENT_CATEGORY_BATTERY,
            )
            servicer.add_component(
                9,
                component_category=PbComponentCategory.COMPONENT_CATEGORY_INVERTER,
            )
            assert set(await microgrid.connections()) == {
                Connection(0, 0),
                Connection(7, 9),
            }

            servicer.add_connection(0, 0)
            assert set(await microgrid.connections()) == {
                Connection(0, 0),
                Connection(7, 9),
                Connection(0, 0),
            }

            servicer.set_connections([(999, 9), (99, 19), (909, 101), (99, 91)])
            for component_id in [999, 99, 19, 909, 101, 91]:
                servicer.add_component(
                    component_id,
                    PbComponentCategory.COMPONENT_CATEGORY_BATTERY,
                )

            assert set(await microgrid.connections()) == {
                Connection(999, 9),
                Connection(99, 19),
                Connection(909, 101),
                Connection(99, 91),
            }

            for component_id in [1, 2, 3, 4, 5, 6, 7, 8]:
                servicer.add_component(
                    component_id,
                    PbComponentCategory.COMPONENT_CATEGORY_BATTERY,
                )

            servicer.set_connections(
                [
                    (1, 2),
                    (2, 3),
                    (2, 4),
                    (2, 5),
                    (4, 3),
                    (4, 5),
                    (4, 6),
                    (5, 4),
                    (5, 7),
                    (5, 8),
                ]
            )
            assert set(await microgrid.connections()) == {
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
            assert set(await microgrid.connections(starts=set(), ends=set())) == {
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

            # include filter for connection start
            assert set(await microgrid.connections(starts={1})) == {Connection(1, 2)}

            assert set(await microgrid.connections(starts={2})) == {
                Connection(2, 3),
                Connection(2, 4),
                Connection(2, 5),
            }
            assert set(await microgrid.connections(starts={3})) == set()

            assert set(await microgrid.connections(starts={4, 5})) == {
                Connection(4, 3),
                Connection(4, 5),
                Connection(4, 6),
                Connection(5, 4),
                Connection(5, 7),
                Connection(5, 8),
            }

            # include filter for connection end
            assert set(await microgrid.connections(ends={1})) == set()

            assert set(await microgrid.connections(ends={3})) == {
                Connection(2, 3),
                Connection(4, 3),
            }

            assert set(await microgrid.connections(ends={2, 4, 5})) == {
                Connection(1, 2),
                Connection(2, 4),
                Connection(2, 5),
                Connection(4, 5),
                Connection(5, 4),
            }

            # different filters combine with AND logic
            assert set(
                await microgrid.connections(starts={1, 2, 4}, ends={4, 5, 6})
            ) == {
                Connection(2, 4),
                Connection(2, 5),
                Connection(4, 5),
                Connection(4, 6),
            }

            assert set(await microgrid.connections(starts={3, 5}, ends={7, 8})) == {
                Connection(5, 7),
                Connection(5, 8),
            }

            assert set(await microgrid.connections(starts={1, 5}, ends={2, 7})) == {
                Connection(1, 2),
                Connection(5, 7),
            }

    async def test_bad_connections(self) -> None:
        """Validate that the client does not apply connection filters itself."""

        class BadServicer(mock_api.MockMicrogridServicer):
            # pylint: disable=unused-argument,invalid-name
            def ListConnections(
                self,
                request: PbConnectionFilter,
                context: grpc.ServicerContext,
            ) -> PbConnectionList:
                """Ignores supplied `PbConnectionFilter`."""
                return PbConnectionList(connections=self._connections)

            def ListAllComponents(
                self, request: Empty, context: grpc.ServicerContext
            ) -> PbComponentList:
                return PbComponentList(components=self._components)

        async with _gprc_server(BadServicer()) as (servicer, microgrid):
            assert not list(await microgrid.connections())
            for component_id in [1, 2, 3, 4, 5, 6, 7, 8, 9]:
                servicer.add_component(
                    component_id,
                    PbComponentCategory.COMPONENT_CATEGORY_BATTERY,
                )
            servicer.set_connections(
                [
                    (1, 2),
                    (1, 9),
                    (2, 3),
                    (3, 4),
                    (4, 5),
                    (5, 6),
                    (6, 7),
                    (7, 6),
                    (7, 9),
                ]
            )

            unfiltered = {
                Connection(1, 2),
                Connection(1, 9),
                Connection(2, 3),
                Connection(3, 4),
                Connection(4, 5),
                Connection(5, 6),
                Connection(6, 7),
                Connection(7, 6),
                Connection(7, 9),
            }

            # because the application of filters is left to the server side,
            # it doesn't matter what filters we set in the client if the
            # server doesn't do its part
            assert set(await microgrid.connections()) == unfiltered
            assert set(await microgrid.connections(starts={1})) == unfiltered
            assert set(await microgrid.connections(ends={9})) == unfiltered
            assert (
                set(await microgrid.connections(starts={1, 7}, ends={3, 9}))
                == unfiltered
            )

    async def test_meter_data(self) -> None:
        """Test the meter_data() method."""
        async with _gprc_server() as (servicer, microgrid):
            servicer.add_component(83, PbComponentCategory.COMPONENT_CATEGORY_METER)
            servicer.add_component(38, PbComponentCategory.COMPONENT_CATEGORY_BATTERY)

            with pytest.raises(ValueError):
                # should raise a ValueError for missing component_id
                await microgrid.meter_data(20)

            with pytest.raises(ValueError):
                # should raise a ValueError for wrong component category
                await microgrid.meter_data(38)
            receiver = await microgrid.meter_data(83)
            await asyncio.sleep(0.2)

        latest = await anext(receiver)
        assert isinstance(latest, MeterData)
        assert latest.component_id == 83

    async def test_battery_data(self) -> None:
        """Test the battery_data() method."""
        async with _gprc_server() as (servicer, microgrid):
            servicer.add_component(83, PbComponentCategory.COMPONENT_CATEGORY_BATTERY)
            servicer.add_component(38, PbComponentCategory.COMPONENT_CATEGORY_INVERTER)

            with pytest.raises(ValueError):
                # should raise a ValueError for missing component_id
                await microgrid.meter_data(20)

            with pytest.raises(ValueError):
                # should raise a ValueError for wrong component category
                await microgrid.meter_data(38)
            receiver = await microgrid.battery_data(83)
            await asyncio.sleep(0.2)

        latest = await anext(receiver)
        assert isinstance(latest, BatteryData)
        assert latest.component_id == 83

    async def test_inverter_data(self) -> None:
        """Test the inverter_data() method."""
        async with _gprc_server() as (servicer, microgrid):
            servicer.add_component(83, PbComponentCategory.COMPONENT_CATEGORY_INVERTER)
            servicer.add_component(38, PbComponentCategory.COMPONENT_CATEGORY_BATTERY)

            with pytest.raises(ValueError):
                # should raise a ValueError for missing component_id
                await microgrid.meter_data(20)

            with pytest.raises(ValueError):
                # should raise a ValueError for wrong component category
                await microgrid.meter_data(38)
            receiver = await microgrid.inverter_data(83)
            await asyncio.sleep(0.2)

        latest = await anext(receiver)
        assert isinstance(latest, InverterData)
        assert latest.component_id == 83

    async def test_ev_charger_data(self) -> None:
        """Test the ev_charger_data() method."""
        async with _gprc_server() as (servicer, microgrid):
            servicer.add_component(
                83, PbComponentCategory.COMPONENT_CATEGORY_EV_CHARGER
            )
            servicer.add_component(38, PbComponentCategory.COMPONENT_CATEGORY_BATTERY)

            with pytest.raises(ValueError):
                # should raise a ValueError for missing component_id
                await microgrid.meter_data(20)

            with pytest.raises(ValueError):
                # should raise a ValueError for wrong component category
                await microgrid.meter_data(38)
            receiver = await microgrid.ev_charger_data(83)
            await asyncio.sleep(0.2)

        latest = await anext(receiver)
        assert isinstance(latest, EVChargerData)
        assert latest.component_id == 83

    async def test_charge(self) -> None:
        """Check if charge is able to charge component."""
        async with _gprc_server() as (servicer, microgrid):
            servicer.add_component(83, PbComponentCategory.COMPONENT_CATEGORY_METER)

            await microgrid.set_power(component_id=83, power_w=12)

            assert servicer.latest_power is not None
            assert servicer.latest_power.component_id == 83
            assert servicer.latest_power.power == 12

    async def test_discharge(self) -> None:
        """Check if discharge is able to discharge component."""
        async with _gprc_server() as (servicer, microgrid):
            servicer.add_component(73, PbComponentCategory.COMPONENT_CATEGORY_METER)

            await microgrid.set_power(component_id=73, power_w=-15)

            assert servicer.latest_power is not None
            assert servicer.latest_power.component_id == 73
            assert servicer.latest_power.power == -15

    async def test_set_bounds(self) -> None:
        """Check if set_bounds is able to set bounds for component."""
        async with _gprc_server() as (servicer, microgrid):
            servicer.add_component(38, PbComponentCategory.COMPONENT_CATEGORY_INVERTER)

            num_calls = 4

            target_metric = PbSetBoundsParam.TargetMetric
            expected_bounds = [
                PbSetBoundsParam(
                    component_id=comp_id,
                    target_metric=target_metric.TARGET_METRIC_POWER_ACTIVE,
                    bounds=PbBounds(lower=-10, upper=2),
                )
                for comp_id in range(num_calls)
            ]
            for cid in range(num_calls):
                await microgrid.set_bounds(cid, -10.0, 2.0)
                await asyncio.sleep(0.1)

        assert len(expected_bounds) == len(servicer.get_bounds())

        def sort_key(
            bound: PbSetBoundsParam,
        ) -> PbSetBoundsParam.TargetMetric.ValueType:
            return bound.target_metric

        assert sorted(servicer.get_bounds(), key=sort_key) == sorted(
            expected_bounds, key=sort_key
        )
