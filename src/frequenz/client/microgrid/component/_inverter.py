# License: MIT
# Copyright © 2024 Frequenz Energy-as-a-Service GmbH

"""Inverter component."""

import dataclasses
import enum
from typing import Any, Literal, Self, TypeAlias

from ._base import Component
from ._category import ComponentCategory


@enum.unique
class InverterType(enum.Enum):
    """The known types of inverters."""

    UNSPECIFIED = 0
    """The type of the inverter is unspecified."""

    BATTERY = 1
    """The inverter is a battery inverter."""

    SOLAR = 2
    """The inverter is a solar inverter."""

    HYBRID = 3
    """The inverter is a hybrid inverter."""


@dataclasses.dataclass(frozen=True, kw_only=True)
class Inverter(Component):
    """An abstract inverter component."""

    category: Literal[ComponentCategory.INVERTER] = ComponentCategory.INVERTER
    """The category of this component."""

    type: InverterType | int
    """The type of this inverter."""

    # pylint: disable-next=unused-argument
    def __new__(cls, *args: Any, **kwargs: Any) -> Self:
        """Prevent instantiation of this class."""
        if cls is Inverter:
            raise TypeError(f"Cannot instantiate {cls.__name__} directly")
        return super().__new__(cls)


@dataclasses.dataclass(frozen=True, kw_only=True)
class UnspecifiedInverter(Inverter):
    """An inverter of an unspecified type."""

    type: Literal[InverterType.UNSPECIFIED] = InverterType.UNSPECIFIED
    """The type of this inverter."""


@dataclasses.dataclass(frozen=True, kw_only=True)
class BatteryInverter(Inverter):
    """A battery inverter."""

    type: Literal[InverterType.BATTERY] = InverterType.BATTERY
    """The type of this inverter."""


@dataclasses.dataclass(frozen=True, kw_only=True)
class SolarInverter(Inverter):
    """A solar inverter."""

    type: Literal[InverterType.SOLAR] = InverterType.SOLAR
    """The type of this inverter."""


@dataclasses.dataclass(frozen=True, kw_only=True)
class HybridInverter(Inverter):
    """A hybrid inverter."""

    type: Literal[InverterType.HYBRID] = InverterType.HYBRID
    """The type of this inverter."""


@dataclasses.dataclass(frozen=True, kw_only=True)
class UnrecognizedInverter(Inverter):
    """An inverter component."""

    type: int
    """The type of this inverter."""


InverterTypes: TypeAlias = (
    UnspecifiedInverter
    | BatteryInverter
    | SolarInverter
    | HybridInverter
    | UnrecognizedInverter
)
"""All possible inverter types."""
