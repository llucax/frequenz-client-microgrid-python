# License: MIT
# Copyright © 2022 Frequenz Energy-as-a-Service GmbH

"""Client for requests to the Microgrid API."""

from __future__ import annotations

import math
from collections.abc import Iterable
from dataclasses import replace
from datetime import datetime, timedelta
from typing import assert_never

from frequenz.api.common.v1.metrics import metric_sample_pb2
from frequenz.api.common.v1.microgrid.components import components_pb2
from frequenz.api.microgrid.v1 import microgrid_pb2, microgrid_pb2_grpc
from frequenz.channels import Receiver
from frequenz.client.base import channel, client, conversion, retry, streaming
from google.protobuf.empty_pb2 import Empty

from ._exception import ClientNotConnected
from ._id import ComponentId
from ._microgrid_info import MicrogridInfo
from ._microgrid_info_proto import microgrid_info_from_proto
from .component._base import Component
from .component._category import ComponentCategory
from .component._component import ComponentTypes
from .component._component_proto import component_from_proto
from .component._connection import ComponentConnection
from .component._connection_proto import component_connection_from_proto
from .component._data_samples import ComponentDataSamples
from .component._data_samples_proto import component_data_sample_from_proto
from .metrics._metric import Metric

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
        self._component_data_samples_broadcasters: dict[
            str,
            streaming.GrpcStreamBroadcaster[
                microgrid_pb2.ReceiveComponentDataStreamResponse, ComponentDataSamples
            ],
        ] = {}
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

    async def list_connections(  # noqa: DOC502 (raises ApiClientError indirectly)
        self,
        *,
        sources: Iterable[ComponentId | Component] = (),
        destinations: Iterable[ComponentId | Component] = (),
    ) -> Iterable[ComponentConnection]:
        """Fetch all the connections present in the local microgrid.

        Electrical components are a part of a microgrid's electrical infrastructure
        are can be connected to each other to form an electrical circuit, which can
        then be represented as a graph.

        The direction of a connection is always away from the grid endpoint, i.e.
        aligned with the direction of positive current according to the passive sign
        convention: https://en.wikipedia.org/wiki/Passive_sign_convention

        The request may be filtered by `source`/`destination` component(s) of individual
        connections.  If provided, the `sources` and `destinations` filters have an
        `AND` relationship between each other, meaning that they are applied serially,
        but an `OR` relationship with other elements in the same list.

        Example:
            If `sources = {1, 2, 3}`, and `destinations = {4,
            5, 6}`, then the result should have all the connections where:

            * Each `source` component ID is either `1`, `2`, OR `3`; **AND**
            * Each `destination` component ID is either `4`, `5`, OR `6`.

        Args:
            sources: The component from which the connections originate.
            destinations: The component at which the connections terminate.

        Returns:
            Iterator whose elements are all the connections in the local microgrid.

        Raises:
            ApiClientError: If the are any errors communicating with the Microgrid API,
                most likely a subclass of
                [GrpcError][frequenz.client.microgrid.GrpcError].
        """
        connection_list = await client.call_stub_method(
            self,
            lambda: self.stub.ListConnections(
                microgrid_pb2.ListConnectionsRequest(
                    starts=map(_get_component_id, sources),
                    ends=map(_get_component_id, destinations),
                ),
                timeout=int(DEFAULT_GRPC_CALL_TIMEOUT),
            ),
            method_name="ListConnections",
        )

        return map(component_connection_from_proto, connection_list.connections)

    async def set_component_power_active(  # noqa: DOC502 (raises ApiClientError indirectly)
        self,
        component: ComponentId | Component,
        power: float,
        *,
        request_lifetime: timedelta | None = None,
        validate_arguments: bool = True,
    ) -> datetime | None:
        """Set the active power output of a component.

        The power output can be negative or positive, depending on whether the component
        is supposed to be discharging or charging, respectively.

        The power output is specified in watts.

        The return value is the timestamp until which the given power command will
        stay in effect. After this timestamp, the component's active power will be
        set to 0, if the API receives no further command to change it before then.
        By default, this timestamp will be set to the current time plus 60 seconds.

        Note:
            The target component may have a resolution of more than 1 W. E.g., an
            inverter may have a resolution of 88 W. In such cases, the magnitude of
            power will be floored to the nearest multiple of the resolution.

        Performs the following sequence actions for the following component
        categories:

        * Inverter: Sends the discharge command to the inverter, making it deliver
          AC power.
        * TODO document missing.

        Args:
            component: The component to set the output active power of.
            power: The output active power level, in watts. Negative values are for
                discharging, and positive values are for charging.
            request_lifetime: The duration, until which the request will stay in effect.
                This duration has to be between 10 seconds and 15 minutes (including
                both limits), otherwise the request will be rejected. It has
                a resolution of a second, so fractions of a second will be rounded for
                `timedelta` objects, and it is interpreted as seconds for `int` objects.
                If not provided, it usually defaults to 60 seconds.
            validate_arguments: Whether to validate the arguments before sending the
                request. If `True` a `ValueError` will be raised if an argument is
                invalid without even sending the request to the server, if `False`, the
                request will be sent without validation.

        Returns:
            The timestamp until which the given power command will stay in effect, or
                `None` if it was not provided.

        Raises:
            ApiClientError: If the are any errors communicating with the Microgrid API,
                most likely a subclass of
                [GrpcError][frequenz.client.microgrid.GrpcError].
        """
        lifetime_seconds = _delta_to_seconds(request_lifetime)

        if validate_arguments:
            _validate_set_power_args(power=power, request_lifetime=lifetime_seconds)

        response = await client.call_stub_method(
            self,
            lambda: self.stub.SetComponentPowerActive(
                microgrid_pb2.SetComponentPowerActiveRequest(
                    component_id=_get_component_id(component),
                    power=power,
                    request_lifetime=lifetime_seconds,
                ),
                timeout=int(DEFAULT_GRPC_CALL_TIMEOUT),
            ),
            method_name="SetComponentPowerActive",
        )

        if response.HasField("valid_until"):
            return conversion.to_datetime(response.valid_until)

        return None

    async def set_component_power_reactive(  # noqa: DOC502 (raises ApiClientError indirectly)
        self,
        component: ComponentId | Component,
        power: float,
        *,
        request_lifetime: timedelta | None = None,
        validate_arguments: bool = True,
    ) -> datetime | None:
        """Set the reactive power output of a component.

        We follow the polarity specified in the IEEE 1459-2010 standard
        definitions, where:

        - Positive reactive is inductive (current is lagging the voltage)
        - Negative reactive is capacitive (current is leading the voltage)

        The power output is specified in VAr.

        The return value is the timestamp until which the given power command will
        stay in effect. After this timestamp, the component's reactive power will
        be set to 0, if the API receives no further command to change it before
        then. By default, this timestamp will be set to the current time plus 60
        seconds.

        Note:
            The target component may have a resolution of more than 1 VAr. E.g., an
            inverter may have a resolution of 88 VAr. In such cases, the magnitude of
            power will be floored to the nearest multiple of the resolution.

        Performs the following sequence actions for the following component
        categories:

        * TODO document missing.

        Args:
            component: The component to set the output reactive power of.
            power: The output reactive power level, in VAr. The standard of polarity is
                as per the IEEE 1459-2010 standard definitions: positive reactive is
                inductive (current is lagging the voltage); negative reactive is
                capacitive (current is leading the voltage).
            request_lifetime: The duration, until which the request will stay in effect.
                This duration has to be between 10 seconds and 15 minutes (including
                both limits), otherwise the request will be rejected. It has
                a resolution of a second, so fractions of a second will be rounded for
                `timedelta` objects, and it is interpreted as seconds for `int` objects.
                If not provided, it usually defaults to 60 seconds.
            validate_arguments: Whether to validate the arguments before sending the
                request. If `True` a `ValueError` will be raised if an argument is
                invalid without even sending the request to the server, if `False`, the
                request will be sent without validation.

        Returns:
            The timestamp until which the given power command will stay in effect, or
                `None` if it was not provided.

        Raises:
            ApiClientError: If the are any errors communicating with the Microgrid API,
                most likely a subclass of
                [GrpcError][frequenz.client.microgrid.GrpcError].
        """
        lifetime_seconds = _delta_to_seconds(request_lifetime)

        if validate_arguments:
            _validate_set_power_args(power=power, request_lifetime=lifetime_seconds)

        response = await client.call_stub_method(
            self,
            lambda: self.stub.SetComponentPowerReactive(
                microgrid_pb2.SetComponentPowerReactiveRequest(
                    component_id=_get_component_id(component),
                    power=power,
                    request_lifetime=lifetime_seconds,
                ),
                timeout=int(DEFAULT_GRPC_CALL_TIMEOUT),
            ),
            method_name="SetComponentPowerReactive",
        )

        if response.HasField("valid_until"):
            return conversion.to_datetime(response.valid_until)

        return None

    # noqa: DOC502 (Raises ApiClientError indirectly)
    async def receive_component_data_samples_stream(
        self,
        component: ComponentId | Component,
        metrics: Iterable[Metric | int],
        *,
        buffer_size: int = 50,
    ) -> Receiver[ComponentDataSamples]:
        """Stream data samples from a component.

        At least one metric must be specified. If no metric is specified, then the
        stream will raise an error.

        Warning:
            Components may not support all metrics. If a component does not support
            a given metric, then the returned data stream will not contain that metric.

            There is no way to tell if a metric is not being received because the
            component does not support it or because there is a transient issue when
            retrieving the metric from the component.

            The supported metrics by a component can even change with time, for example,
            if a component is updated with new firmware.

        Args:
            component: The component to stream data from.
            metrics: List of metrics to return. Only the specified metrics will be
                returned.
            buffer_size: The maximum number of messages to buffer in the returned
                receiver. After this limit is reached, the oldest messages will be
                dropped.

        Returns:
            The data stream from the component.
        """
        component_id = _get_component_id(component)
        metrics_set = frozenset([_get_metric_value(m) for m in metrics])
        key = f"{component_id}-{hash(metrics_set)}"
        broadcaster = self._component_data_samples_broadcasters.get(key)
        if broadcaster is None:
            client_id = hex(id(self))[2:]
            stream_name = f"microgrid-client-{client_id}-component-data-{key}"
            create_filter = (
                microgrid_pb2.ReceiveComponentDataStreamRequest.ComponentDataStreamFilter
            )
            broadcaster = streaming.GrpcStreamBroadcaster(
                stream_name,
                lambda: aiter(
                    self.stub.ReceiveComponentDataStream(
                        microgrid_pb2.ReceiveComponentDataStreamRequest(
                            component_id=_get_component_id(component),
                            filter=create_filter(metrics=metrics_set),
                        ),
                        timeout=int(DEFAULT_GRPC_CALL_TIMEOUT),
                    )
                ),
                lambda msg: component_data_sample_from_proto(msg.data),
                retry_strategy=self._retry_strategy,
            )
            self._component_data_samples_broadcasters[key] = broadcaster
        return broadcaster.new_receiver(maxsize=buffer_size)


def _get_component_id(component: ComponentId | Component) -> int:
    """Get the component ID from a component or component ID."""
    match component:
        case ComponentId():
            return int(component)
        case Component():
            return int(component.id)
        case unexpected:
            assert_never(unexpected)


def _get_metric_value(metric: Metric | int) -> metric_sample_pb2.Metric.ValueType:
    """Get the metric ID from a metric or metric ID."""
    match metric:
        case Metric():
            return metric_sample_pb2.Metric.ValueType(metric.value)
        case int():
            return metric_sample_pb2.Metric.ValueType(metric)
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


def _delta_to_seconds(delta: timedelta | None) -> int | None:
    """Convert a `timedelta` to seconds (or `None` if `None`)."""
    return round(delta.total_seconds()) if delta is not None else None


def _validate_set_power_args(*, power: float, request_lifetime: int | None) -> None:
    """Validate the request lifetime."""
    if math.isnan(power):
        raise ValueError("power cannot be NaN")
    if request_lifetime is not None:
        minimum_lifetime = 10  # 10 seconds
        maximum_lifetime = 900  # 15 minutes
        if not minimum_lifetime <= request_lifetime <= maximum_lifetime:
            raise ValueError(
                "request_lifetime must be between 10 seconds and 15 minutes"
            )
