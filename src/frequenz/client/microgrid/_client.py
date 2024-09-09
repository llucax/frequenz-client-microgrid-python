# License: MIT
# Copyright © 2022 Frequenz Energy-as-a-Service GmbH

"""Client for requests to the Microgrid API."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import replace
from typing import Any, assert_never

from frequenz.api.common.v1.microgrid.components import components_pb2
from frequenz.api.microgrid import microgrid_pb2_grpc
from frequenz.api.microgrid.v1 import microgrid_pb2, microgrid_pb2_grpc
from frequenz.client.base import channel, client, retry, streaming
from google.protobuf.empty_pb2 import Empty

from ._exception import ClientNotConnected
from ._id import ComponentId
from ._microgrid_info import MicrogridInfo
from ._microgrid_info_proto import microgrid_info_from_proto
from .component._base import Component
from .component._category import ComponentCategory
from .component._component import ComponentTypes
from .component._component_proto import component_from_proto

DEFAULT_GRPC_CALL_TIMEOUT = 60.0
"""The default timeout for gRPC calls made by this client (in seconds)."""

DEFAULT_CHANNEL_OPTIONS = replace(
    channel.ChannelOptions(), ssl=channel.SslOptions(enabled=False)
)
"""The default channel options for the microgrid API client.

These are the same defaults as the common default options but with SSL disabled, as the
microgrid API does not use SSL by default.
"""


class MicrogridApiClient(client.BaseApiClient[microgrid_pb2_grpc.MicrogridStub]):
    """A microgrid API client."""

    def __init__(
        self,
        server_url: str,
        *,
        channel_defaults: channel.ChannelOptions = DEFAULT_CHANNEL_OPTIONS,
        connect: bool = True,
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
            channel_defaults: The default options use to create the channel when not
                specified in the URL.
            connect: Whether to connect to the server as soon as a client instance is
                created. If `False`, the client will not connect to the server until
                [connect()][frequenz.client.base.client.BaseApiClient.connect] is
                called.
            retry_strategy: The retry strategy to use to reconnect when the connection
                to the streaming method is lost. By default a linear backoff strategy
                is used.
        """
        super().__init__(
            server_url,
            microgrid_pb2_grpc.MicrogridStub,
            connect=connect,
            channel_defaults=channel_defaults,
        )
        self._broadcasters: dict[int, streaming.GrpcStreamBroadcaster[Any, Any]] = {}
        self._retry_strategy = retry_strategy

    @property
    def stub(self) -> microgrid_pb2_grpc.MicrogridAsyncStub:
        """The gRPC stub for the API."""
        if self.channel is None or self._stub is None:
            raise ClientNotConnected(server_url=self.server_url, operation="stub")
        # This type: ignore is needed because we need to cast the sync stub to
        # the async stub, but we can't use cast because the async stub doesn't
        # actually exists to the eyes of the interpreter, it only exists for the
        # type-checker, so it can only be used for type hints.
        return self._stub  # type: ignore

    async def get_microgrid_info(  # noqa: DOC502 (raises ApiClientError indirectly)
        self,
    ) -> MicrogridInfo:
        """Fetch the information about the local microgrid.

        This consists of information that describes the overall microgrid, as opposed to
        its electrical components or sensors, e.g., the microgrid ID, location.

        Returns:
            The information about the local microgrid.

        Raises:
            ApiClientError: If the are any errors communicating with the Microgrid API,
                most likely a subclass of
                [GrpcError][frequenz.client.microgrid.GrpcError].
        """
        microgrid = await client.call_stub_method(
            self,
            lambda: self.stub.GetMicrogridMetadata(
                Empty(),
                timeout=int(DEFAULT_GRPC_CALL_TIMEOUT),
            ),
            method_name="GetMicrogridMetadata",
        )

        return microgrid_info_from_proto(microgrid.microgrid)

    async def list_components(  # noqa: DOC502 (raises ApiClientError indirectly)
        self,
        *,
        components: Iterable[ComponentId | Component] = (),
        categories: Iterable[ComponentCategory | int] = (),
    ) -> Iterable[ComponentTypes]:
        """Fetch all the components present in the local microgrid.

        Electrical components are a part of a microgrid's electrical infrastructure
        are can be connected to each other to form an electrical circuit, which can
        then be represented as a graph.

        If provided, the filters for component and categories have an `AND`
        relationship with one another, meaning that they are applied serially,
        but the elements within a single filter list have an `OR` relationship with
        each other.

        Example:
            If `ids = {1, 2, 3}`, and `categories = {ComponentCategory.INVERTER,
            ComponentCategory.BATTERY}`, then the results will consist of elements that
            have:

            * The IDs 1, `OR` 2, `OR` 3; `AND`
            * Are of the categories `ComponentCategory.INVERTER` `OR`
              `ComponentCategory.BATTERY`.

        If a filter list is empty, then that filter is not applied.

        Args:
            components: The components to fetch. See the method description for details.
            categories: The categories of the components to fetch. See the method
                description for details.

        Returns:
            Iterator whose elements are all the components in the local microgrid.

        Raises:
            ApiClientError: If the are any errors communicating with the Microgrid API,
                most likely a subclass of
                [GrpcError][frequenz.client.microgrid.GrpcError].
        """
        component_list = await client.call_stub_method(
            self,
            lambda: self.stub.ListComponents(
                microgrid_pb2.ListComponentsRequest(
                    component_ids=map(_get_component_id, components),
                    categories=map(_get_category_value, categories),
                ),
                timeout=int(DEFAULT_GRPC_CALL_TIMEOUT),
            ),
            method_name="ListComponents",
        )

        return map(component_from_proto, component_list.components)


def _get_component_id(component: ComponentId | Component) -> int:
    """Get the component ID from a component or component ID."""
    match component:
        case ComponentId():
            return int(component)
        case Component():
            return int(component.id)
        case unexpected:
            assert_never(unexpected)


def _get_category_value(
    category: ComponentCategory | int,
) -> components_pb2.ComponentCategory.ValueType:
    """Get the category value from a component or component category."""
    match category:
        case ComponentCategory():
            return components_pb2.ComponentCategory.ValueType(category.value)
        case int():
            return components_pb2.ComponentCategory.ValueType(category)
        case unexpected:
            assert_never(unexpected)
