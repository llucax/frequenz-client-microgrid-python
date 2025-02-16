# License: MIT
# Copyright © 2022 Frequenz Energy-as-a-Service GmbH

"""Defines states of components that can be used in a microgrid."""

from enum import Enum
from typing import Self

from frequenz.microgrid.betterproto.frequenz.api.microgrid import (
    battery,
    ev_charger,
    inverter,
)


class BatteryComponentState(Enum):
    """Component states of a battery."""

    UNSPECIFIED = battery.ComponentState.COMPONENT_STATE_UNSPECIFIED
    """Unspecified component state."""

    OFF = battery.ComponentState.COMPONENT_STATE_OFF
    """The battery is switched off."""

    IDLE = battery.ComponentState.COMPONENT_STATE_IDLE
    """The battery is idle."""

    CHARGING = battery.ComponentState.COMPONENT_STATE_CHARGING
    """The battery is consuming electrical energy."""

    DISCHARGING = battery.ComponentState.COMPONENT_STATE_DISCHARGING
    """The battery is generating electrical energy."""

    ERROR = battery.ComponentState.COMPONENT_STATE_ERROR
    """The battery is in a faulty state."""

    LOCKED = battery.ComponentState.COMPONENT_STATE_LOCKED
    """The battery is online, but currently unavailable.

    Possibly due to a pre-scheduled maintenance, or waiting for a resource to be loaded.
    """

    SWITCHING_ON = battery.ComponentState.COMPONENT_STATE_SWITCHING_ON
    """
    The battery is starting up and needs some time to become fully operational.
    """

    SWITCHING_OFF = battery.ComponentState.COMPONENT_STATE_SWITCHING_OFF
    """The battery is switching off and needs some time to fully shut down."""

    UNKNOWN = battery.ComponentState.COMPONENT_STATE_UNKNOWN
    """A state is provided by the component, but it is not one of the above states."""

    @classmethod
    def from_pb(cls, state: battery.ComponentState) -> Self:
        """Convert a protobuf state value to this enum.

        Args:
            state: The protobuf component state to convert.

        Returns:
            The enum value corresponding to the protobuf message.
        """
        try:
            return cls(state)
        except ValueError:
            return cls(cls.UNKNOWN)


class BatteryRelayState(Enum):
    """Relay states of a battery."""

    UNSPECIFIED = battery.RelayState.RELAY_STATE_UNSPECIFIED
    """Unspecified relay state."""

    OPENED = battery.RelayState.RELAY_STATE_OPENED
    """The relays are open, and the DC power line to the inverter is disconnected."""

    PRECHARGING = battery.RelayState.RELAY_STATE_PRECHARGING
    """The relays are closing, and the DC power line to the inverter is being connected."""

    CLOSED = battery.RelayState.RELAY_STATE_CLOSED
    """The relays are closed, and the DC power line to the inverter is connected."""

    ERROR = battery.RelayState.RELAY_STATE_ERROR
    """The relays are in an error state."""

    LOCKED = battery.RelayState.RELAY_STATE_LOCKED
    """The relays are locked, and should be available to accept commands shortly."""

    @classmethod
    def from_pb(cls, state: battery.RelayState) -> Self:
        """Convert a protobuf state value to this enum.

        Args:
            state: The protobuf component state to convert.

        Returns:
            The enum value corresponding to the protobuf message.
        """
        try:
            return cls(state)
        except ValueError:
            return cls(cls.UNSPECIFIED)


class EVChargerCableState(Enum):
    """Cable states of an EV Charger."""

    UNSPECIFIED = ev_charger.CableState.CABLE_STATE_UNSPECIFIED
    """Unspecified cable state."""

    UNPLUGGED = ev_charger.CableState.CABLE_STATE_UNPLUGGED
    """The cable is unplugged."""

    CHARGING_STATION_PLUGGED = (
        ev_charger.CableState.CABLE_STATE_CHARGING_STATION_PLUGGED
    )
    """The cable is plugged into the charging station."""

    CHARGING_STATION_LOCKED = ev_charger.CableState.CABLE_STATE_CHARGING_STATION_LOCKED
    """The cable is plugged into the charging station and locked."""

    EV_PLUGGED = ev_charger.CableState.CABLE_STATE_EV_PLUGGED
    """The cable is plugged into the EV."""

    EV_LOCKED = ev_charger.CableState.CABLE_STATE_EV_LOCKED
    """The cable is plugged into the EV and locked."""

    @classmethod
    def from_pb(cls, state: ev_charger.CableState) -> Self:
        """Convert a protobuf state value to this enum.

        Args:
            state: The protobuf cable state to convert.

        Returns:
            The enum value corresponding to the protobuf message.
        """
        try:
            return cls(state)
        except ValueError:
            return cls(cls.UNSPECIFIED)


class EVChargerComponentState(Enum):
    """Component State of an EV Charger."""

    UNSPECIFIED = ev_charger.ComponentState.COMPONENT_STATE_UNSPECIFIED
    """Unspecified component state."""

    STARTING = ev_charger.ComponentState.COMPONENT_STATE_STARTING
    """The component is starting."""

    NOT_READY = ev_charger.ComponentState.COMPONENT_STATE_NOT_READY
    """The component is not ready."""

    READY = ev_charger.ComponentState.COMPONENT_STATE_READY
    """The component is ready."""

    CHARGING = ev_charger.ComponentState.COMPONENT_STATE_CHARGING
    """The component is charging."""

    DISCHARGING = ev_charger.ComponentState.COMPONENT_STATE_DISCHARGING
    """The component is discharging."""

    ERROR = ev_charger.ComponentState.COMPONENT_STATE_ERROR
    """The component is in error state."""

    AUTHORIZATION_REJECTED = (
        ev_charger.ComponentState.COMPONENT_STATE_AUTHORIZATION_REJECTED
    )
    """The component rejected authorization."""

    INTERRUPTED = ev_charger.ComponentState.COMPONENT_STATE_INTERRUPTED
    """The component is interrupted."""

    UNKNOWN = ev_charger.ComponentState.COMPONENT_STATE_UNKNOWN
    """A state is provided by the component, but it is not one of the above states."""

    @classmethod
    def from_pb(cls, state: ev_charger.ComponentState) -> Self:
        """Convert a protobuf state value to this enum.

        Args:
            state: The protobuf component state to convert.

        Returns:
            The enum value corresponding to the protobuf message.
        """
        try:
            return cls(state)
        except ValueError:
            return cls(cls.UNKNOWN)


class InverterComponentState(Enum):
    """Component states of an inverter."""

    UNSPECIFIED = inverter.ComponentState.COMPONENT_STATE_UNSPECIFIED
    """Unspecified component state."""

    OFF = inverter.ComponentState.COMPONENT_STATE_OFF
    """Inverter is switched off."""

    SWITCHING_ON = inverter.ComponentState.COMPONENT_STATE_SWITCHING_ON
    """The inverter is starting up and needs some time to become fully operational."""

    SWITCHING_OFF = inverter.ComponentState.COMPONENT_STATE_SWITCHING_OFF
    """The inverter is switching off and needs some time to fully shut down."""

    STANDBY = inverter.ComponentState.COMPONENT_STATE_STANDBY
    """The inverter is in a standby state, and is disconnected from the grid.

    When connected to the grid, it run a few tests, and move to the `IDLE` state.
    """

    IDLE = inverter.ComponentState.COMPONENT_STATE_IDLE
    """The inverter is idle."""

    CHARGING = inverter.ComponentState.COMPONENT_STATE_CHARGING
    """The inverter is consuming electrical energy to charge batteries.

    Applicable to `BATTERY` and `HYBRID` inverters only.
    """

    DISCHARGING = inverter.ComponentState.COMPONENT_STATE_DISCHARGING
    """The inverter is generating electrical energy."""

    ERROR = inverter.ComponentState.COMPONENT_STATE_ERROR
    """The inverter is in a faulty state."""

    UNAVAILABLE = inverter.ComponentState.COMPONENT_STATE_UNAVAILABLE
    """The inverter is online, but currently unavailable.

    Possibly due to a pre- scheduled maintenance.
    """

    UNKNOWN = inverter.ComponentState.COMPONENT_STATE_UNKNOWN
    """A state is provided by the component, but it is not one of the above states."""

    @classmethod
    def from_pb(cls, state: inverter.ComponentState) -> Self:
        """Convert a protobuf state value to this enum.

        Args:
            state: The protobuf component state to convert.

        Returns:
            The enum value corresponding to the protobuf message.
        """
        try:
            return cls(state)
        except ValueError:
            return cls(cls.UNKNOWN)
