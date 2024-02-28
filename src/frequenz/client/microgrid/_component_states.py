# License: MIT
# Copyright © 2022 Frequenz Energy-as-a-Service GmbH

"""Defines states of components that can be used in a microgrid."""

from enum import Enum
from typing import Self

# pylint: disable=no-name-in-module
from frequenz.api.microgrid.ev_charger_pb2 import CableState as PbCableState
from frequenz.api.microgrid.ev_charger_pb2 import ComponentState as PbComponentState

# pylint: enable=no-name-in-module


class EVChargerCableState(Enum):
    """Cable states of an EV Charger."""

    UNSPECIFIED = PbCableState.CABLE_STATE_UNSPECIFIED
    """Unspecified cable state."""

    UNPLUGGED = PbCableState.CABLE_STATE_UNPLUGGED
    """The cable is unplugged."""

    CHARGING_STATION_PLUGGED = PbCableState.CABLE_STATE_CHARGING_STATION_PLUGGED
    """The cable is plugged into the charging station."""

    CHARGING_STATION_LOCKED = PbCableState.CABLE_STATE_CHARGING_STATION_LOCKED
    """The cable is plugged into the charging station and locked."""

    EV_PLUGGED = PbCableState.CABLE_STATE_EV_PLUGGED
    """The cable is plugged into the EV."""

    EV_LOCKED = PbCableState.CABLE_STATE_EV_LOCKED
    """The cable is plugged into the EV and locked."""

    @classmethod
    def from_pb(cls, evc_state: PbCableState.ValueType) -> Self:
        """Convert a protobuf CableState value to EVChargerCableState enum.

        Args:
            evc_state: protobuf cable state to convert.

        Returns:
            Enum value corresponding to the protobuf message.
        """
        if not any(t.value == evc_state for t in EVChargerCableState):
            return cls(cls.UNSPECIFIED)

        return cls(evc_state)


class EVChargerComponentState(Enum):
    """Component State of an EV Charger."""

    UNSPECIFIED = PbComponentState.COMPONENT_STATE_UNSPECIFIED
    """Unspecified component state."""

    STARTING = PbComponentState.COMPONENT_STATE_STARTING
    """The component is starting."""

    NOT_READY = PbComponentState.COMPONENT_STATE_NOT_READY
    """The component is not ready."""

    READY = PbComponentState.COMPONENT_STATE_READY
    """The component is ready."""

    CHARGING = PbComponentState.COMPONENT_STATE_CHARGING
    """The component is charging."""

    DISCHARGING = PbComponentState.COMPONENT_STATE_DISCHARGING
    """The component is discharging."""

    ERROR = PbComponentState.COMPONENT_STATE_ERROR
    """The component is in error state."""

    AUTHORIZATION_REJECTED = PbComponentState.COMPONENT_STATE_AUTHORIZATION_REJECTED
    """The component rejected authorization."""

    INTERRUPTED = PbComponentState.COMPONENT_STATE_INTERRUPTED
    """The component is interrupted."""

    @classmethod
    def from_pb(cls, evc_state: PbComponentState.ValueType) -> Self:
        """Convert a protobuf ComponentState value to EVChargerComponentState enum.

        Args:
            evc_state: protobuf component state to convert.

        Returns:
            Enum value corresponding to the protobuf message.
        """
        if not any(t.value == evc_state for t in EVChargerComponentState):
            return cls(cls.UNSPECIFIED)

        return cls(evc_state)
