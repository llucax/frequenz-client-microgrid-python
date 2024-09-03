# License: MIT
# Copyright © 2022 Frequenz Energy-as-a-Service GmbH

"""Client for requests to the Microgrid API."""

import asyncio
import logging
from collections.abc import AsyncIterator, Awaitable, Callable, Iterable, Set
from dataclasses import replace
from typing import Any, TypeVar, cast

import grpc.aio
from frequenz.api.common import components_pb2, metrics_pb2
from frequenz.api.microgrid import microgrid_pb2, microgrid_pb2_grpc
from frequenz.channels import Receiver
from frequenz.client.base import channel, retry, streaming
from google.protobuf.empty_pb2 import Empty
from google.protobuf.timestamp_pb2 import Timestamp

from ._component import (
    Component,
    ComponentCategory,
    component_category_from_protobuf,
    component_metadata_from_protobuf,
    component_type_from_protobuf,
)
from ._component_data import (
    BatteryData,
    ComponentData,
    EVChargerData,
    InverterData,
    MeterData,
)
from ._connection import Connection
from ._constants import RECEIVER_MAX_SIZE
from ._exception import ApiClientError
from ._metadata import Location, Metadata

DEFAULT_GRPC_CALL_TIMEOUT = 60.0
"""The default timeout for gRPC calls made by this client (in seconds)."""

_ComponentDataT = TypeVar("_ComponentDataT", bound=ComponentData)
"""Type variable resolving to any ComponentData sub-class."""

_logger = logging.getLogger(__name__)


DEFAULT_CHANNEL_OPTIONS = replace(
    channel.ChannelOptions(), ssl=channel.SslOptions(enabled=False)
)
"""The default channel options for the microgrid API client.

These are the same defaults as the common default options but with SSL disabled, as the
microgrid API does not use SSL by default.
"""


class MicrogridApiClient:
    """A microgrid API client."""

    def __init__(
        self,
        server_url: str,
        *,
        channel_options: channel.ChannelOptions = DEFAULT_CHANNEL_OPTIONS,
        retry_strategy: retry.Strategy | None = None,
    ) -> None:
        """Initialize the class instance.

        Args:
            server_url: The location of the microgrid API server in the form of a URL.
                The following format is expected:
                "grpc://hostname{:`port`}{?ssl=`ssl`}",
                where the `port` should be an int between 0 and 65535 (defaulting to
                9090) and `ssl` should be a boolean (defaulting to `false`).
                For example: `grpc://localhost:1090?ssl=true`.
            channel_options: The default options use to create the channel when not
                specified in the URL.
            retry_strategy: The retry strategy to use to reconnect when the connection
                to the streaming method is lost. By default a linear backoff strategy
                is used.
        """
        self._server_url = server_url
        """The location of the microgrid API server as a URL."""

        self.stub = microgrid_pb2_grpc.MicrogridStub(
            channel.parse_grpc_uri(server_url, defaults=channel_options)
        )
        """The gRPC stub for the microgrid API."""

        self._broadcasters: dict[int, streaming.GrpcStreamBroadcaster[Any, Any]] = {}
        self._retry_strategy = retry_strategy

    @property
    def server_url(self) -> str:
        """The server location in URL format."""
        return self._server_url

    async def components(self) -> Iterable[Component]:
        """Fetch all the components present in the microgrid.

        Returns:
            Iterator whose elements are all the components in the microgrid.

        Raises:
            ApiClientError: If the are any errors communicating with the Microgrid API,
                most likely a subclass of
                [GrpcError][frequenz.client.microgrid.GrpcError].
        """
        try:
            # grpc.aio is missing types and mypy thinks this is not awaitable,
            # but it is
            component_list = await cast(
                Awaitable[microgrid_pb2.ComponentList],
                self.stub.ListComponents(
                    microgrid_pb2.ComponentFilter(),
                    timeout=int(DEFAULT_GRPC_CALL_TIMEOUT),
                ),
            )
        except grpc.aio.AioRpcError as grpc_error:
            raise ApiClientError.from_grpc_error(
                server_url=self._server_url,
                operation="ListComponents",
                grpc_error=grpc_error,
            ) from grpc_error

        components_only = filter(
            lambda c: c.category
            is not components_pb2.ComponentCategory.COMPONENT_CATEGORY_SENSOR,
            component_list.components,
        )
        result: Iterable[Component] = map(
            lambda c: Component(
                c.id,
                component_category_from_protobuf(c.category),
                component_type_from_protobuf(c.category, c.inverter),
                component_metadata_from_protobuf(c.category, c.grid),
            ),
            components_only,
        )

        return result

    async def metadata(self) -> Metadata:
        """Fetch the microgrid metadata.

        If there is an error fetching the metadata, the microgrid ID and
        location will be set to None.

        Returns:
            the microgrid metadata.
        """
        microgrid_metadata: microgrid_pb2.MicrogridMetadata | None = None
        try:
            microgrid_metadata = await cast(
                Awaitable[microgrid_pb2.MicrogridMetadata],
                self.stub.GetMicrogridMetadata(
                    Empty(),
                    timeout=int(DEFAULT_GRPC_CALL_TIMEOUT),
                ),
            )
        except grpc.aio.AioRpcError:
            _logger.exception("The microgrid metadata is not available.")

        if not microgrid_metadata:
            return Metadata()

        location: Location | None = None
        if microgrid_metadata.location:
            location = Location(
                latitude=microgrid_metadata.location.latitude,
                longitude=microgrid_metadata.location.longitude,
            )

        return Metadata(microgrid_id=microgrid_metadata.microgrid_id, location=location)

    async def connections(
        self,
        starts: Set[int] = frozenset(),
        ends: Set[int] = frozenset(),
    ) -> Iterable[Connection]:
        """Fetch the connections between components in the microgrid.

        Args:
            starts: if set and non-empty, only include connections whose start
                value matches one of the provided component IDs
            ends: if set and non-empty, only include connections whose end value
                matches one of the provided component IDs

        Returns:
            Microgrid connections matching the provided start and end filters.

        Raises:
            ApiClientError: If the are any errors communicating with the Microgrid API,
                most likely a subclass of
                [GrpcError][frequenz.client.microgrid.GrpcError].
        """
        connection_filter = microgrid_pb2.ConnectionFilter(starts=starts, ends=ends)
        try:
            valid_components, all_connections = await asyncio.gather(
                self.components(),
                # grpc.aio is missing types and mypy thinks this is not
                # awaitable, but it is
                cast(
                    Awaitable[microgrid_pb2.ConnectionList],
                    self.stub.ListConnections(
                        connection_filter,
                        timeout=int(DEFAULT_GRPC_CALL_TIMEOUT),
                    ),
                ),
            )
        except grpc.aio.AioRpcError as grpc_error:
            raise ApiClientError.from_grpc_error(
                server_url=self._server_url,
                operation="ListConnections",
                grpc_error=grpc_error,
            ) from grpc_error
        # Filter out the components filtered in `components` method.
        # id=0 is an exception indicating grid component.
        valid_ids = {c.component_id for c in valid_components}
        valid_ids.add(0)

        connections = filter(
            lambda c: (c.start in valid_ids and c.end in valid_ids),
            all_connections.connections,
        )

        result: Iterable[Connection] = map(
            lambda c: Connection(c.start, c.end), connections
        )

        return result

    async def _new_component_data_receiver(
        self,
        *,
        component_id: int,
        expected_category: ComponentCategory,
        transform: Callable[[microgrid_pb2.ComponentData], _ComponentDataT],
        maxsize: int,
    ) -> Receiver[_ComponentDataT]:
        """Return a new broadcaster receiver for a given `component_id`.

        If a broadcaster for the given `component_id` doesn't exist, it creates a new
        one.

        Args:
            component_id: id of the component to get data for.
            expected_category: Category of the component to get data for.
            transform: A method for transforming raw component data into the
                desired output type.
            maxsize: Size of the receiver's buffer.

        Returns:
            The new receiver for the given `component_id`.
        """
        await self._expect_category(
            component_id,
            expected_category,
        )

        broadcaster = self._broadcasters.get(component_id)
        if broadcaster is None:
            broadcaster = streaming.GrpcStreamBroadcaster(
                f"raw-component-data-{component_id}",
                # We need to cast here because grpc says StreamComponentData is
                # a grpc.CallIterator[microgrid_pb2.ComponentData] which is not an
                # AsyncIterator, but it is a grpc.aio.UnaryStreamCall[...,
                # microgrid_pb2.ComponentData], which it is.
                lambda: cast(
                    AsyncIterator[microgrid_pb2.ComponentData],
                    self.stub.StreamComponentData(
                        microgrid_pb2.ComponentIdParam(id=component_id)
                    ),
                ),
                transform,
                retry_strategy=self._retry_strategy,
            )
            self._broadcasters[component_id] = broadcaster
        return broadcaster.new_receiver(maxsize=maxsize)

    async def _expect_category(
        self,
        component_id: int,
        expected_category: ComponentCategory,
    ) -> None:
        """Check if the given component_id is of the expected type.

        Raises:
            ValueError: if the given id is unknown or has a different type.

        Args:
            component_id: Component id to check.
            expected_category: Component category that the given id is expected
                to have.
        """
        try:
            comp = next(
                comp
                for comp in await self.components()
                if comp.component_id == component_id
            )
        except StopIteration as exc:
            raise ValueError(
                f"Unable to find component with id {component_id}"
            ) from exc

        if comp.category != expected_category:
            raise ValueError(
                f"Component id {component_id} is a {comp.category.name.lower()}"
                f", not a {expected_category.name.lower()}."
            )

    async def meter_data(  # noqa: DOC502 (ValueError is raised indirectly by _expect_category)
        self,
        component_id: int,
        maxsize: int = RECEIVER_MAX_SIZE,
    ) -> Receiver[MeterData]:
        """Return a channel receiver that provides a `MeterData` stream.

        Raises:
            ValueError: if the given id is unknown or has a different type.

        Args:
            component_id: id of the meter to get data for.
            maxsize: Size of the receiver's buffer.

        Returns:
            A channel receiver that provides realtime meter data.
        """
        return await self._new_component_data_receiver(
            component_id=component_id,
            expected_category=ComponentCategory.METER,
            transform=MeterData.from_proto,
            maxsize=maxsize,
        )

    async def battery_data(  # noqa: DOC502 (ValueError is raised indirectly by _expect_category)
        self,
        component_id: int,
        maxsize: int = RECEIVER_MAX_SIZE,
    ) -> Receiver[BatteryData]:
        """Return a channel receiver that provides a `BatteryData` stream.

        Raises:
            ValueError: if the given id is unknown or has a different type.

        Args:
            component_id: id of the battery to get data for.
            maxsize: Size of the receiver's buffer.

        Returns:
            A channel receiver that provides realtime battery data.
        """
        return await self._new_component_data_receiver(
            component_id=component_id,
            expected_category=ComponentCategory.BATTERY,
            transform=BatteryData.from_proto,
            maxsize=maxsize,
        )

    async def inverter_data(  # noqa: DOC502 (ValueError is raised indirectly by _expect_category)
        self,
        component_id: int,
        maxsize: int = RECEIVER_MAX_SIZE,
    ) -> Receiver[InverterData]:
        """Return a channel receiver that provides an `InverterData` stream.

        Raises:
            ValueError: if the given id is unknown or has a different type.

        Args:
            component_id: id of the inverter to get data for.
            maxsize: Size of the receiver's buffer.

        Returns:
            A channel receiver that provides realtime inverter data.
        """
        return await self._new_component_data_receiver(
            component_id=component_id,
            expected_category=ComponentCategory.INVERTER,
            transform=InverterData.from_proto,
            maxsize=maxsize,
        )

    async def ev_charger_data(  # noqa: DOC502 (ValueError is raised indirectly by _expect_category)
        self,
        component_id: int,
        maxsize: int = RECEIVER_MAX_SIZE,
    ) -> Receiver[EVChargerData]:
        """Return a channel receiver that provides an `EvChargeData` stream.

        Raises:
            ValueError: if the given id is unknown or has a different type.

        Args:
            component_id: id of the ev charger to get data for.
            maxsize: Size of the receiver's buffer.

        Returns:
            A channel receiver that provides realtime ev charger data.
        """
        return await self._new_component_data_receiver(
            component_id=component_id,
            expected_category=ComponentCategory.EV_CHARGER,
            transform=EVChargerData.from_proto,
            maxsize=maxsize,
        )

    async def set_power(self, component_id: int, power_w: float) -> None:
        """Send request to the Microgrid to set power for component.

        If power > 0, then component will be charged with this power.
        If power < 0, then component will be discharged with this power.
        If power == 0, then stop charging or discharging component.


        Args:
            component_id: id of the component to set power.
            power_w: power to set for the component.

        Raises:
            ApiClientError: If the are any errors communicating with the Microgrid API,
                most likely a subclass of
                [GrpcError][frequenz.client.microgrid.GrpcError].
        """
        try:
            await cast(
                Awaitable[Empty],
                self.stub.SetPowerActive(
                    microgrid_pb2.SetPowerActiveParam(
                        component_id=component_id, power=power_w
                    ),
                    timeout=int(DEFAULT_GRPC_CALL_TIMEOUT),
                ),
            )
        except grpc.aio.AioRpcError as grpc_error:
            raise ApiClientError.from_grpc_error(
                server_url=self._server_url,
                operation="SetPowerActive",
                grpc_error=grpc_error,
            ) from grpc_error

    async def set_bounds(
        self,
        component_id: int,
        lower: float,
        upper: float,
    ) -> None:
        """Send `SetBoundsParam`s received from a channel to the Microgrid service.

        Args:
            component_id: ID of the component to set bounds for.
            lower: Lower bound to be set for the component.
            upper: Upper bound to be set for the component.

        Raises:
            ValueError: when upper bound is less than 0, or when lower bound is
                greater than 0.
            ApiClientError: If the are any errors communicating with the Microgrid API,
                most likely a subclass of
                [GrpcError][frequenz.client.microgrid.GrpcError].
        """
        if upper < 0:
            raise ValueError(f"Upper bound {upper} must be greater than or equal to 0.")
        if lower > 0:
            raise ValueError(f"Lower bound {lower} must be less than or equal to 0.")

        target_metric = (
            microgrid_pb2.SetBoundsParam.TargetMetric.TARGET_METRIC_POWER_ACTIVE
        )
        try:
            await cast(
                Awaitable[Timestamp],
                self.stub.AddInclusionBounds(
                    microgrid_pb2.SetBoundsParam(
                        component_id=component_id,
                        target_metric=target_metric,
                        bounds=metrics_pb2.Bounds(lower=lower, upper=upper),
                    ),
                    timeout=int(DEFAULT_GRPC_CALL_TIMEOUT),
                ),
            )
        except grpc.aio.AioRpcError as grpc_error:
            raise ApiClientError.from_grpc_error(
                server_url=self._server_url,
                operation="AddInclusionBounds",
                grpc_error=grpc_error,
            ) from grpc_error
