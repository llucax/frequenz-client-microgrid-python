# License: MIT
# Copyright © 2024 Frequenz Energy-as-a-Service GmbH

"""Precharger component."""

import dataclasses
from typing import Literal

from ._base import Component
from ._category import ComponentCategory


@dataclasses.dataclass(frozen=True, kw_only=True)
class Precharger(Component):
    """A precharger component."""

    category: Literal[ComponentCategory.PRECHARGER] = ComponentCategory.PRECHARGER
    """The category of this component."""
