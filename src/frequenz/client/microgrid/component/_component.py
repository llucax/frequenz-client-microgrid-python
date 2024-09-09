# License: MIT
# Copyright © 2024 Frequenz Energy-as-a-Service GmbH

"""All known component types."""

from typing import TypeAlias

from ._battery import BatteryTypes
from ._chp import Chp
from ._converter import Converter
from ._crypto_miner import CryptoMiner
from ._electrolyzer import Electrolyzer
from ._ev_charger import EvChargerTypes
from ._fuse import Fuse
from ._grid_connection_point import GridConnectionPoint
from ._hvac import Hvac
from ._inverter import InverterTypes
from ._meter import Meter
from ._precharger import Precharger
from ._problematic import ProblematicComponentTypes
from ._relay import Relay
from ._voltage_transformer import VoltageTransformer

ComponentTypes: TypeAlias = (
    BatteryTypes
    | Chp
    | Converter
    | CryptoMiner
    | Electrolyzer
    | EvChargerTypes
    | Fuse
    | GridConnectionPoint
    | Hvac
    | InverterTypes
    | Meter
    | Precharger
    | ProblematicComponentTypes
    | Relay
    | VoltageTransformer
)
"""All possible component types."""
