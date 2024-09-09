# License: MIT
# Copyright © 2024 Frequenz Energy-as-a-Service GmbH

"""Meter component."""

import dataclasses
from typing import Literal

from ._base import Component
from ._category import ComponentCategory


@dataclasses.dataclass(frozen=True, kw_only=True)
class Meter(Component):
    """A measuring meter component."""

    category: Literal[ComponentCategory.METER] = ComponentCategory.METER
    """The category of this component."""
