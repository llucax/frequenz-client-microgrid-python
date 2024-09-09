# License: MIT
# Copyright © 2024 Frequenz Energy-as-a-Service GmbH

"""Electrolyzer component."""

import dataclasses
from typing import Literal

from ._base import Component
from ._category import ComponentCategory


@dataclasses.dataclass(frozen=True, kw_only=True)
class Electrolyzer(Component):
    """A electrolyzer component."""

    category: Literal[ComponentCategory.ELECTROLYZER] = ComponentCategory.ELECTROLYZER
    """The category of this component."""
