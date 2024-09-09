# License: MIT
# Copyright © 2024 Frequenz Energy-as-a-Service GmbH

"""Electric vehicle (EV) charger component."""

import dataclasses
import enum
from typing import Any, Literal, Self, TypeAlias

from ._base import Component
from ._category import ComponentCategory


@enum.unique
class EvChargerType(enum.Enum):
    """The known types of electric vehicle (EV) chargers."""

    UNSPECIFIED = 0
    """The type of the EV charger is unspecified."""

    AC = 1
    """The EV charging station supports AC charging only."""

    DC = 2
    """The EV charging station supports DC charging only."""

    HYBRID = 3
    """The EV charging station supports both AC and DC."""


@dataclasses.dataclass(frozen=True, kw_only=True)
class EvCharger(Component):
    """An abstract EV charger component."""

    category: Literal[ComponentCategory.EV_CHARGER] = ComponentCategory.EV_CHARGER
    """The category of this component."""

    type: EvChargerType | int
    """The type of this EV charger."""

    # pylint: disable-next=unused-argument
    def __new__(cls, *args: Any, **kwargs: Any) -> Self:
        """Prevent instantiation of this class."""
        if cls is EvCharger:
            raise TypeError(f"Cannot instantiate {cls.__name__} directly")
        return super().__new__(cls)


@dataclasses.dataclass(frozen=True, kw_only=True)
class UnspecifiedEvCharger(EvCharger):
    """An EV charger of an unspecified type."""

    type: Literal[EvChargerType.UNSPECIFIED] = EvChargerType.UNSPECIFIED
    """The type of this EV charger."""


@dataclasses.dataclass(frozen=True, kw_only=True)
class AcEvCharger(EvCharger):
    """An EV charger that supports AC charging only."""

    type: Literal[EvChargerType.AC] = EvChargerType.AC
    """The type of this EV charger."""


@dataclasses.dataclass(frozen=True, kw_only=True)
class DcEvCharger(EvCharger):
    """An EV charger that supports DC charging only."""

    type: Literal[EvChargerType.DC] = EvChargerType.DC
    """The type of this EV charger."""


@dataclasses.dataclass(frozen=True, kw_only=True)
class HybridEvCharger(EvCharger):
    """An EV charger that supports both AC and DC charging."""

    type: Literal[EvChargerType.HYBRID] = EvChargerType.HYBRID
    """The type of this EV charger."""


@dataclasses.dataclass(frozen=True, kw_only=True)
class UnrecognizedEvCharger(EvCharger):
    """An EV charger of an unrecognized type."""

    type: int
    """The type of this EV charger."""


EvChargerTypes: TypeAlias = (
    UnspecifiedEvCharger
    | AcEvCharger
    | DcEvCharger
    | HybridEvCharger
    | UnrecognizedEvCharger
)
"""All possible EV charger types."""
