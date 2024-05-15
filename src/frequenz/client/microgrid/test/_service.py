# License: MIT
# Copyright © 2024 Frequenz Energy-as-a-Service GmbH

"""Fake service to simulate a microgrid API service."""

import dataclasses
from dataclasses import dataclass, replace
from datetime import datetime, timezone
from random import shuffle

from frequenz.microgrid.betterproto.frequenz.api.common.components import (
    ComponentCategory,
    InverterType,
)
from frequenz.microgrid.betterproto.frequenz.api.microgrid import (
    Component,
    ComponentData,
    ComponentFilter,
    ComponentIdParam,
    ComponentList,
    Connection,
    ConnectionFilter,
    ConnectionList,
    MicrogridMetadata,
    SetBoundsParam,
    SetPowerActiveParam,
    SetPowerReactiveParam,
)


@dataclass
class FakeService:
    """Dispatch mock service for testing."""

    components: list[Component] = dataclasses.field(default_factory=list)
    """List of components served by this service."""

    connections: list[Connection] = dataclasses.field(default_factory=list)
    """List of connections served by this service."""

    bounds: list[SetBoundsParam] = dataclasses.field(default_factory=list)
    """List of bounds served by this service."""

    def __init__(
        self,
        *,
        components: list[tuple[int, ComponentCategory]] | None = None,
        connections: list[tuple[int, int]] | None = None,
    ):
        if components is not None:
            self.set_components(components)
        if connections is not None:
            self.set_connections(connections)

        self._latest_power: SetPowerActiveParam | None = None

    def add_component(
        self,
        component_id: int,
        component_category: ComponentCategory,
        max_current: float | None = None,
        inverter_type: InverterType = InverterType.INVERTER_TYPE_UNSPECIFIED,
    ) -> None:
        """Add a component to the mock service."""
        if component_category == ComponentCategory.COMPONENT_CATEGORY_INVERTER:
            self._components.append(
                Component(
                    id=component_id,
                    category=component_category,
                    inverter=InverterMetadata(type=inverter_type),
                )
            )
        elif (
            component_category == ComponentCategory.COMPONENT_CATEGORY_GRID
            and max_current is not None
        ):
            self._components.append(
                Component(
                    id=component_id,
                    category=component_category,
                    grid=GridMetadata(rated_fuse_current=int(max_current)),
                )
            )
        else:
            self._components.append(
                Component(id=component_id, category=component_category)
            )

    def add_connection(self, start: int, end: int) -> None:
        """Add a connection to the mock service."""
        self._connections.append(Connection(start=start, end=end))

    def set_components(self, components: list[tuple[int, ComponentCategory]]) -> None:
        """Set components to mock service, dropping existing."""
        self._components.clear()
        self._components.extend(
            map(lambda c: Component(id=c[0], category=c[1]), components)
        )

    def set_connections(self, connections: list[tuple[int, int]]) -> None:
        """Set connections to mock service, dropping existing."""
        self._connections.clear()
        self._connections.extend(
            map(lambda c: Connection(start=c[0], end=c[1]), connections)
        )

    # pylint: disable=invalid-name
    async def ListMicrogridDispatches(
        self, request: PBDispatchListRequest
    ) -> DispatchList:
        """List microgrid dispatches.

        Args:
            request: The request.

        Returns:
            The dispatch list.
        """
        return DispatchList(
            dispatches=map(
                lambda d: d.to_protobuf(),
                filter(
                    lambda d: self._filter_dispatch(d, request),
                    self.dispatches,
                ),
            )
        )
