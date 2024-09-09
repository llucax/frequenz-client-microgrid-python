# License: MIT
# Copyright © 2024 Frequenz Energy-as-a-Service GmbH

"""Converter component."""

import dataclasses
from typing import Literal

from ._base import Component
from ._category import ComponentCategory


@dataclasses.dataclass(frozen=True, kw_only=True)
class Converter(Component):
    """An AC-DC converter component."""

    category: Literal[ComponentCategory.CONVERTER] = ComponentCategory.CONVERTER
    """The category of this component."""
