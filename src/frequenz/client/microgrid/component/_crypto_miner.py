# License: MIT
# Copyright © 2024 Frequenz Energy-as-a-Service GmbH

"""Crypto miner component."""

import dataclasses
from typing import Literal

from ._base import Component
from ._category import ComponentCategory


@dataclasses.dataclass(frozen=True, kw_only=True)
class CryptoMiner(Component):
    """A crypto miner component."""

    category: Literal[ComponentCategory.CRYPTO_MINER] = ComponentCategory.CRYPTO_MINER
    """The category of this component."""
