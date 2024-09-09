# License: MIT
# Copyright © 2024 Frequenz Energy-as-a-Service GmbH

"""The component categories that can be used in a microgrid."""

import enum


@enum.unique
class ComponentCategory(enum.Enum):
    """The known categories of components that can be present in a microgrid."""

    UNSPECIFIED = 0
    """The component category is unspecified, probably due to an error in the message."""

    GRID = 1
    """The point where the local microgrid is connected to the grid."""

    METER = 2
    """A meter, for measuring electrical metrics, e.g., current, voltage, etc."""

    INVERTER = 3
    """An electricity generator, with batteries or solar energy."""

    CONVERTER = 4
    """A DC-DC converter."""

    BATTERY = 5
    """A storage system for electrical energy, used by inverters."""

    EV_CHARGER = 6
    """A station for charging electrical vehicles."""

    CRYPTO_MINER = 8
    """A crypto miner."""

    ELECTROLYZER = 9
    """An electrolyzer for converting water into hydrogen and oxygen."""

    CHP = 10
    """A heat and power combustion plant (CHP stands for combined heat and power)."""

    RELAY = 11
    """A relay.

    Relays generally have two states: open (connected) and closed (disconnected).
    They are generally placed in front of a component, e.g., an inverter, to
    control whether the component is connected to the grid or not.
    """

    PRECHARGER = 12
    """A precharge module.

    Precharging involves gradually ramping up the DC voltage to prevent any
    potential damage to sensitive electrical components like capacitors.

    While many inverters and batteries come equipped with in-built precharging
    mechanisms, some may lack this feature. In such cases, we need to use
    external precharging modules.
    """

    FUSE = 13
    """A fuse."""

    VOLTAGE_TRANSFORMER = 14
    """A voltage transformer.

    Voltage transformers are used to step up or step down the voltage, keeping
    the power somewhat constant by increasing or decreasing the current.  If voltage is
    stepped up, current is stepped down, and vice versa.

    Note:
        Voltage transformers have efficiency losses, so the output power is
        always less than the input power.
    """

    HVAC = 15
    """A Heating, Ventilation, and Air Conditioning (HVAC) system."""
