# License: MIT
# Copyright © 2024 Frequenz Energy-as-a-Service GmbH

"""Fuse component."""

import dataclasses
from typing import Literal

from ._base import Component
from ._category import ComponentCategory


@dataclasses.dataclass(frozen=True, kw_only=True)
class Fuse(Component):
    """A fuse component.

    Fuses are used to protect components from overcurrents.
    """

    category: Literal[ComponentCategory.FUSE] = ComponentCategory.FUSE
    """The category of this component."""

    rated_current: int
    """The rated current of the fuse in amperes.

    This is the maximum current that the fuse can withstand for a long time. This limit
    applies to currents both flowing in or out of each of the 3 phases individually.

    In other words, a current `i`A at one of the phases of the node must comply with the
    following constraint:
    `-rated_fuse_current <= i <= rated_fuse_current`
    """
