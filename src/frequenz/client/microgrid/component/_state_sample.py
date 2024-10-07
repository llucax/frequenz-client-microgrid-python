# License: MIT
# Copyright © 2024 Frequenz Energy-as-a-Service GmbH

"""Definition of a component state."""

import enum
from dataclasses import dataclass
from datetime import datetime


@enum.unique
class ComponentStateCode(enum.Enum):
    """The various states that a component can be in."""

    UNSPECIFIED = 0
    """The state is unspecified (this should not be normally used)."""

    UNKNOWN = 1
    """The component is in an unknown or undefined condition.

    This is used when the state can be retrieved from the component but it doesn't match
    any known state.
    """

    UNAVAILABLE = 2
    """The component is temporarily unavailable for operation."""

    SWITCHING_OFF = 3
    """The component is in the process of switching off."""

    OFF = 4
    """The component has successfully switched off."""

    SWITCHING_ON = 5
    """The component is in the process of switching on."""

    STANDBY = 6
    """The component is in standby mode and not immediately ready for operation."""

    READY = 7
    """The component is fully operational and ready for use."""

    CHARGING = 8
    """The component is actively consuming energy."""

    DISCHARGING = 9
    """The component is actively producing or releasing energy."""

    ERROR = 10
    """The component is in an error state and may need attention."""

    EV_CHARGING_CABLE_UNPLUGGED = 20
    """The EV charging cable is unplugged from the charging station."""

    EV_CHARGING_CABLE_PLUGGED_AT_STATION = 21
    """The EV charging cable is plugged into the charging station."""

    EV_CHARGING_CABLE_PLUGGED_AT_EV = 22
    """The EV charging cable is plugged into the vehicle."""

    EV_CHARGING_CABLE_LOCKED_AT_STATION = 23
    """The EV charging cable is locked at the charging station end."""

    EV_CHARGING_CABLE_LOCKED_AT_EV = 24
    """The EV charging cable is locked at the vehicle end."""

    RELAY_OPEN = 30
    """The relay is in an open state, meaning no current can flow through."""

    RELAY_CLOSED = 31
    """The relay is in a closed state, allowing current to flow."""

    PRECHARGER_OPEN = 40
    """The precharger circuit is open, meaning it's not currently active."""

    PRECHARGER_PRECHARGING = 41
    """The precharger is in a precharging state, preparing the main circuit for activation."""

    PRECHARGER_CLOSED = 42
    """The precharger circuit is closed, allowing full current to flow to the main circuit."""


@enum.unique
class ComponentErrorCode(enum.Enum):
    """The various errors that a component can report."""

    UNSPECIFIED = 0
    """The error is unspecified (this should not be normally used)."""

    UNKNOWN = 1
    """The component is reporting an unknown or undefined error.

    This is used when the error can be retrieved from the component but it doesn't match
    any known error.
    """

    SWITCH_ON_FAULT = 2
    """The component could not be switched on."""

    UNDERVOLTAGE = 3
    """The component is operating under the minimum rated voltage."""

    OVERVOLTAGE = 4
    """The component is operating over the maximum rated voltage."""

    OVERCURRENT = 5
    """The component is drawing more current than the maximum rated value."""

    OVERCURRENT_CHARGING = 6
    """The component's consumption current is over the maximum rated value during charging."""

    OVERCURRENT_DISCHARGING = 7
    """The component's production current is over the maximum rated value during discharging."""

    OVERTEMPERATURE = 8
    """The component is operating over the maximum rated temperature."""

    UNDERTEMPERATURE = 9
    """The component is operating under the minimum rated temperature."""

    HIGH_HUMIDITY = 10
    """The component is exposed to high humidity levels over the maximum rated value."""

    FUSE_ERROR = 11
    """The component's fuse has blown."""

    PRECHARGE_ERROR = 12
    """The component's precharge unit has failed."""

    PLAUSIBILITY_ERROR = 13
    """Plausibility issues within the system involving this component."""

    UNDERVOLTAGE_SHUTDOWN = 14
    """System shutdown due to undervoltage involving this component."""

    EV_UNEXPECTED_PILOT_FAILURE = 15
    """Unexpected pilot failure in an electric vehicle component."""

    FAULT_CURRENT = 16
    """Fault current detected in the component."""

    SHORT_CIRCUIT = 17
    """Short circuit detected in the component."""

    CONFIG_ERROR = 18
    """Configuration error related to the component."""

    ILLEGAL_COMPONENT_STATE_CODE_REQUESTED = 19
    """Illegal state requested for the component."""

    HARDWARE_INACCESSIBLE = 20
    """Hardware of the component is inaccessible."""

    INTERNAL = 21
    """Internal error within the component."""

    UNAUTHORIZED = 22
    """The component is unauthorized to perform the last requested action."""

    EV_CHARGING_CABLE_UNPLUGGED_FROM_STATION = 40
    """EV cable was abruptly unplugged from the charging station."""

    EV_CHARGING_CABLE_UNPLUGGED_FROM_EV = 41
    """EV cable was abruptly unplugged from the vehicle."""

    EV_CHARGING_CABLE_LOCK_FAILED = 42
    """EV cable lock failure."""

    EV_CHARGING_CABLE_INVALID = 43
    """Invalid EV cable."""

    EV_CONSUMER_INCOMPATIBLE = 44
    """Incompatible EV plug."""

    BATTERY_IMBALANCE = 50
    """Battery system imbalance."""

    BATTERY_LOW_SOH = 51
    """Low state of health (SOH) detected in the battery."""

    BATTERY_BLOCK_ERROR = 52
    """Battery block error."""

    BATTERY_CONTROLLER_ERROR = 53
    """Battery controller error."""

    BATTERY_RELAY_ERROR = 54
    """Battery relay error."""

    BATTERY_CALIBRATION_NEEDED = 56
    """Battery calibration is needed."""

    RELAY_CYCLE_LIMIT_REACHED = 60
    """Relays have been cycled for the maximum number of times."""


@dataclass(frozen=True, kw_only=True)
class ComponentStateSample:
    """A collection of the state, warnings, and errors for a component at a specific time."""

    sampled_at: datetime
    """The time at which this state was sampled."""

    states: frozenset[ComponentStateCode | int]
    """The set of states of the component.

    If the reported state is not known by the client (it could happen when using an
    older version of the client with a newer version of the server), it will be
    represented as an `int` and **not** the
    [`ComponentStateCode.UNKNOWN`][frequenz.client.microgrid.component.ComponentStateCode.UNKNOWN]
    value (this value is used only when the state is not known by the server).
    """

    warnings: frozenset[ComponentErrorCode | int]
    """The set of warnings for the component."""

    errors: frozenset[ComponentErrorCode | int]
    """The set of errors for the component.

    This set will only contain errors if the component is in an error state.
    """
