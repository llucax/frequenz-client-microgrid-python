# Copyright © 2024 Frequenz Energy-as-a-Service GmbH

"""Conversion from and to protobuf messages."""

from frequenz.microgrid.betterproto.frequenz.api.common import components
from frequenz.microgrid.betterproto.frequenz.api.microgrid import grid, inverter

from ._component import (
    ComponentCategory,
    ComponentType,
    Fuse,
    GridMetadata,
    InverterType,
)


def component_category_from_protobuf(
    component_category: components.ComponentCategory,
) -> ComponentCategory:
    """Convert a protobuf ComponentCategory message to ComponentCategory enum.

    For internal-only use by the `microgrid` package.

    Args:
        component_category: protobuf enum to convert

    Returns:
        Enum value corresponding to the protobuf message.

    Raises:
        ValueError: if `component_category` is a sensor (this is not considered
            a valid component category as it does not form part of the
            microgrid itself)
    """
    if component_category == components.ComponentCategory.COMPONENT_CATEGORY_SENSOR:
        raise ValueError("Cannot create a component from a sensor!")

    if not any(t.value == component_category for t in ComponentCategory):
        return ComponentCategory.NONE

    return ComponentCategory(component_category)


def component_metadata_from_protobuf(
    component_category: components.ComponentCategory,
    component_metadata: grid.Metadata,
) -> GridMetadata | None:
    """Convert a protobuf GridMetadata message to GridMetadata class.

    For internal-only use by the `microgrid` package.

    Args:
        component_category: category the type belongs to.
        component_metadata: protobuf metadata to fetch type from.

    Returns:
        GridMetadata instance corresponding to the protobuf message.
    """
    if component_category == components.ComponentCategory.COMPONENT_CATEGORY_GRID:
        max_current = component_metadata.rated_fuse_current
        fuse = Fuse(max_current)
        return GridMetadata(fuse)

    return None


def component_type_from_protobuf(
    component_category: components.ComponentCategory,
    component_metadata: inverter.Metadata,
) -> ComponentType | None:
    """Convert a protobuf InverterType message to Component enum.

    For internal-only use by the `microgrid` package.

    Args:
        component_category: category the type belongs to.
        component_metadata: protobuf metadata to fetch type from.

    Returns:
        Enum value corresponding to the protobuf message.
    """
    # ComponentType values in the protobuf definition are not unique across categories
    # as of v0.11.0, so we need to check the component category first, before doing any
    # component type checks.
    if component_category == components.ComponentCategory.COMPONENT_CATEGORY_INVERTER:
        if not any(int(t.value) == int(component_metadata.type) for t in InverterType):
            return None

        return InverterType(component_metadata.type)

    return None
