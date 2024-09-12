# License: MIT
# Copyright © 2022 Frequenz Energy-as-a-Service GmbH

"""Client for requests to the Microgrid API."""

from __future__ import annotations

from dataclasses import replace
from typing import Any

from frequenz.api.microgrid import microgrid_pb2_grpc
from frequenz.client.base import channel, client, retry, streaming

from ._exception import ClientNotConnected

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
