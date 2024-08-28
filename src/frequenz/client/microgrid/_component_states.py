# License: MIT
# Copyright © 2022 Frequenz Energy-as-a-Service GmbH

"""Defines states of components that can be used in a microgrid."""

from enum import Enum
from typing import Self

from frequenz.api.microgrid.battery_pb2 import ComponentState as PbBatteryComponentState
from frequenz.api.microgrid.battery_pb2 import RelayState as PbBatteryRelayState
from frequenz.api.microgrid.ev_charger_pb2 import CableState as PbEvCableState
from frequenz.api.microgrid.ev_charger_pb2 import ComponentState as PbEvComponentState
from frequenz.api.microgrid.inverter_pb2 import (
    ComponentState as PbInverterComponentState,
)


class BatteryComponentState(Enum):
    """Component states of a battery."""

    UNSPECIFIED = PbBatteryComponentState.COMPONENT_STATE_UNSPECIFIED
    """Unspecified component state."""

    OFF = PbBatteryComponentState.COMPONENT_STATE_OFF
    """The battery is switched off."""

    IDLE = PbBatteryComponentState.COMPONENT_STATE_IDLE
    """The battery is idle."""

    CHARGING = PbBatteryComponentState.COMPONENT_STATE_CHARGING
    """The battery is consuming electrical energy."""

    DISCHARGING = PbBatteryComponentState.COMPONENT_STATE_DISCHARGING
    """The battery is generating electrical energy."""

    ERROR = PbBatteryComponentState.COMPONENT_STATE_ERROR
    """The battery is in a faulty state."""

    LOCKED = PbBatteryComponentState.COMPONENT_STATE_LOCKED
    """The battery is online, but currently unavailable.

    Possibly due to a pre-scheduled maintenance, or waiting for a resource to be loaded.
    """

    SWITCHING_ON = PbBatteryComponentState.COMPONENT_STATE_SWITCHING_ON
    """
    The battery is starting up and needs some time to become fully operational.
    """

    SWITCHING_OFF = PbBatteryComponentState.COMPONENT_STATE_SWITCHING_OFF
    """The battery is switching off and needs some time to fully shut down."""

    UNKNOWN = PbBatteryComponentState.COMPONENT_STATE_UNKNOWN
    """A state is provided by the component, but it is not one of the above states."""

    @classmethod
    def from_pb(cls, state: PbBatteryComponentState.ValueType) -> Self:
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

    UNSPECIFIED = PbBatteryRelayState.RELAY_STATE_UNSPECIFIED
    """Unspecified relay state."""

    OPENED = PbBatteryRelayState.RELAY_STATE_OPENED
    """The relays are open, and the DC power line to the inverter is disconnected."""

    PRECHARGING = PbBatteryRelayState.RELAY_STATE_PRECHARGING
    """The relays are closing, and the DC power line to the inverter is being connected."""

    CLOSED = PbBatteryRelayState.RELAY_STATE_CLOSED
    """The relays are closed, and the DC power line to the inverter is connected."""

    ERROR = PbBatteryRelayState.RELAY_STATE_ERROR
    """The relays are in an error state."""

    LOCKED = PbBatteryRelayState.RELAY_STATE_LOCKED
    """The relays are locked, and should be available to accept commands shortly."""

    @classmethod
    def from_pb(cls, state: PbBatteryRelayState.ValueType) -> Self:
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

    UNSPECIFIED = PbEvCableState.CABLE_STATE_UNSPECIFIED
    """Unspecified cable state."""

    UNPLUGGED = PbEvCableState.CABLE_STATE_UNPLUGGED
    """The cable is unplugged."""

    CHARGING_STATION_PLUGGED = PbEvCableState.CABLE_STATE_CHARGING_STATION_PLUGGED
    """The cable is plugged into the charging station."""

    CHARGING_STATION_LOCKED = PbEvCableState.CABLE_STATE_CHARGING_STATION_LOCKED
    """The cable is plugged into the charging station and locked."""

    EV_PLUGGED = PbEvCableState.CABLE_STATE_EV_PLUGGED
    """The cable is plugged into the EV."""

    EV_LOCKED = PbEvCableState.CABLE_STATE_EV_LOCKED
    """The cable is plugged into the EV and locked."""

    @classmethod
    def from_pb(cls, state: PbEvCableState.ValueType) -> Self:
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

    UNSPECIFIED = PbEvComponentState.COMPONENT_STATE_UNSPECIFIED
    """Unspecified component state."""

    STARTING = PbEvComponentState.COMPONENT_STATE_STARTING
    """The component is starting."""

    NOT_READY = PbEvComponentState.COMPONENT_STATE_NOT_READY
    """The component is not ready."""

    READY = PbEvComponentState.COMPONENT_STATE_READY
    """The component is ready."""

    CHARGING = PbEvComponentState.COMPONENT_STATE_CHARGING
    """The component is charging."""

    DISCHARGING = PbEvComponentState.COMPONENT_STATE_DISCHARGING
    """The component is discharging."""

    ERROR = PbEvComponentState.COMPONENT_STATE_ERROR
    """The component is in error state."""

    AUTHORIZATION_REJECTED = PbEvComponentState.COMPONENT_STATE_AUTHORIZATION_REJECTED
    """The component rejected authorization."""

    INTERRUPTED = PbEvComponentState.COMPONENT_STATE_INTERRUPTED
    """The component is interrupted."""

    UNKNOWN = PbEvComponentState.COMPONENT_STATE_UNKNOWN
    """A state is provided by the component, but it is not one of the above states."""

    @classmethod
    def from_pb(cls, state: PbEvComponentState.ValueType) -> Self:
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

    UNSPECIFIED = PbInverterComponentState.COMPONENT_STATE_UNSPECIFIED
    """Unspecified component state."""

    OFF = PbInverterComponentState.COMPONENT_STATE_OFF
    """Inverter is switched off."""

    SWITCHING_ON = PbInverterComponentState.COMPONENT_STATE_SWITCHING_ON
    """The PbInverteris starting up and needs some time to become fully operational."""

    SWITCHING_OFF = PbInverterComponentState.COMPONENT_STATE_SWITCHING_OFF
    """The PbInverteris switching off and needs some time to fully shut down."""

    STANDBY = PbInverterComponentState.COMPONENT_STATE_STANDBY
    """The PbInverteris in a standby state, and is disconnected from the grid.

    When connected to the grid, it run a few tests, and move to the `IDLE` state.
    """

    IDLE = PbInverterComponentState.COMPONENT_STATE_IDLE
    """The inverter is idle."""

    CHARGING = PbInverterComponentState.COMPONENT_STATE_CHARGING
    """The inverter is consuming electrical energy to charge batteries.

    Applicable to `BATTERY` and `HYBRID` inverters only.
    """

    DISCHARGING = PbInverterComponentState.COMPONENT_STATE_DISCHARGING
    """The inverter is generating electrical energy."""

    ERROR = PbInverterComponentState.COMPONENT_STATE_ERROR
    """The inverter is in a faulty state."""

    UNAVAILABLE = PbInverterComponentState.COMPONENT_STATE_UNAVAILABLE
    """The inverter is online, but currently unavailable.

    Possibly due to a pre- scheduled maintenance.
    """

    UNKNOWN = PbInverterComponentState.COMPONENT_STATE_UNKNOWN
    """A state is provided by the component, but it is not one of the above states."""

    @classmethod
    def from_pb(cls, state: PbInverterComponentState.ValueType) -> Self:
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
