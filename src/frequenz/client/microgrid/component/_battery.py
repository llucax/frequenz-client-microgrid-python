# License: MIT
# Copyright © 2024 Frequenz Energy-as-a-Service GmbH

"""Battery component."""

import dataclasses
import enum
from typing import Any, Literal, Self, TypeAlias

from ._base import Component
from ._category import ComponentCategory


@enum.unique
class BatteryType(enum.Enum):
    """The known types of batteries."""

    UNSPECIFIED = 0
    """The battery type is unspecified."""

    LI_ION = 1
    """Lithium-ion (Li-ion) battery."""

    NA_ION = 2
    """Sodium-ion (Na-ion) battery."""


@dataclasses.dataclass(frozen=True, kw_only=True)
class Battery(Component):
    """An abstract battery component."""

    category: Literal[ComponentCategory.BATTERY] = ComponentCategory.BATTERY
    """The category of this component."""

    # pylint: disable-next=unused-argument
    def __new__(cls, *args: Any, **kwargs: Any) -> Self:
        """Prevent instantiation of this class."""
        if cls is Battery:
            raise TypeError(f"Cannot instantiate {cls.__name__} directly")
        return super().__new__(cls)


@dataclasses.dataclass(frozen=True, kw_only=True)
class UnspecifiedBattery(Battery):
    """A battery of a unspecified type."""


@dataclasses.dataclass(frozen=True, kw_only=True)
class LiIonBattery(Battery):
    """A Li-ion battery."""


@dataclasses.dataclass(frozen=True, kw_only=True)
class NaIonBattery(Battery):
    """A Na-ion battery."""


@dataclasses.dataclass(frozen=True, kw_only=True)
class UnrecognizedBattery(Battery):
    """A battery of an unrecognized type."""

    type: int
    """The type of this battery."""


BatteryTypes: TypeAlias = (
    LiIonBattery | NaIonBattery | UnrecognizedBattery | UnspecifiedBattery
)
"""All possible battery types."""
