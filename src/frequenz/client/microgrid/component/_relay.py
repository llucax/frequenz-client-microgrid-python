# License: MIT
# Copyright © 2024 Frequenz Energy-as-a-Service GmbH

"""Relay component."""

import dataclasses
from typing import Literal

from ._base import Component
from ._category import ComponentCategory


@dataclasses.dataclass(frozen=True, kw_only=True)
class Relay(Component):
    """A relay component."""

    category: Literal[ComponentCategory.RELAY] = ComponentCategory.RELAY
    """The category of this component."""
