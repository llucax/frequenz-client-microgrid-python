# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Definition of component states."""

import enum
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime

from frequenz.api.common.v1alpha8.microgrid.electrical_components import (
    electrical_components_pb2,
)


@enum.unique
class ElectricalComponentStateCode(enum.Enum):
    """The various states that a component can be in."""

    UNSPECIFIED = electrical_components_pb2.ELECTRICAL_COMPONENT_STATE_CODE_UNSPECIFIED
    """The state is unspecified (this should not be normally used)."""

    UNKNOWN = electrical_components_pb2.ELECTRICAL_COMPONENT_STATE_CODE_UNKNOWN
    """The component is in an unknown or undefined condition.

    This is used when the state can be retrieved from the component but it doesn't match
    any known state.
    """

    UNAVAILABLE = electrical_components_pb2.ELECTRICAL_COMPONENT_STATE_CODE_UNAVAILABLE
    """The component is temporarily unavailable for operation."""

    SWITCHING_OFF = (
        electrical_components_pb2.ELECTRICAL_COMPONENT_STATE_CODE_SWITCHING_OFF
    )
    """The component is in the process of switching off."""

    OFF = electrical_components_pb2.ELECTRICAL_COMPONENT_STATE_CODE_OFF
    """The component has successfully switched off."""

    SWITCHING_ON = (
        electrical_components_pb2.ELECTRICAL_COMPONENT_STATE_CODE_SWITCHING_ON
    )
    """The component is in the process of switching on."""

    STANDBY = electrical_components_pb2.ELECTRICAL_COMPONENT_STATE_CODE_STANDBY
    """The component is in standby mode and not immediately ready for operation."""

    READY = electrical_components_pb2.ELECTRICAL_COMPONENT_STATE_CODE_READY
    """The component is fully operational and ready for use."""

    CHARGING = electrical_components_pb2.ELECTRICAL_COMPONENT_STATE_CODE_CHARGING
    """The component is actively consuming energy."""

    DISCHARGING = electrical_components_pb2.ELECTRICAL_COMPONENT_STATE_CODE_DISCHARGING
    """The component is actively producing or releasing energy."""

    ERROR = electrical_components_pb2.ELECTRICAL_COMPONENT_STATE_CODE_ERROR
    """The component is in an error state and may need attention."""

    EV_CHARGING_CABLE_UNPLUGGED = (
        electrical_components_pb2.ELECTRICAL_COMPONENT_STATE_CODE_EV_CHARGING_CABLE_UNPLUGGED
    )
    """The EV charging cable is unplugged from the charging station."""

    EV_CHARGING_CABLE_PLUGGED_AT_STATION = (
        electrical_components_pb2.ELECTRICAL_COMPONENT_STATE_CODE_EV_CHARGING_CABLE_PLUGGED_AT_STATION  # noqa: E501
    )
    """The EV charging cable is plugged into the charging station."""

    EV_CHARGING_CABLE_PLUGGED_AT_EV = (
        electrical_components_pb2.ELECTRICAL_COMPONENT_STATE_CODE_EV_CHARGING_CABLE_PLUGGED_AT_EV
    )
    """The EV charging cable is plugged into the vehicle."""

    EV_CHARGING_CABLE_LOCKED_AT_STATION = (
        electrical_components_pb2.ELECTRICAL_COMPONENT_STATE_CODE_EV_CHARGING_CABLE_LOCKED_AT_STATION  # noqa: E501
    )
    """The EV charging cable is locked at the charging station end."""

    EV_CHARGING_CABLE_LOCKED_AT_EV = (
        electrical_components_pb2.ELECTRICAL_COMPONENT_STATE_CODE_EV_CHARGING_CABLE_LOCKED_AT_EV
    )
    """The EV charging cable is locked at the vehicle end."""

    RELAY_OPEN = electrical_components_pb2.ELECTRICAL_COMPONENT_STATE_CODE_RELAY_OPEN
    """The relay is in an open state, meaning no current can flow through."""

    RELAY_CLOSED = (
        electrical_components_pb2.ELECTRICAL_COMPONENT_STATE_CODE_RELAY_CLOSED
    )
    """The relay is in a closed state, allowing current to flow."""

    PRECHARGER_OPEN = (
        electrical_components_pb2.ELECTRICAL_COMPONENT_STATE_CODE_PRECHARGER_OPEN
    )
    """The precharger circuit is open, meaning it's not currently active."""

    PRECHARGER_PRECHARGING = (
        electrical_components_pb2.ELECTRICAL_COMPONENT_STATE_CODE_PRECHARGER_PRECHARGING
    )
    """The precharger is in a precharging state, preparing the main circuit for activation."""

    PRECHARGER_CLOSED = (
        electrical_components_pb2.ELECTRICAL_COMPONENT_STATE_CODE_PRECHARGER_CLOSED
    )
    """The precharger circuit is closed, allowing full current to flow to the main circuit."""


@enum.unique
class ElectricalComponentDiagnosticCode(enum.Enum):
    """The various diagnostic codes that can occur for an electrical component.

    These diagnostic codes can be used to refer to warnings or errors that are reported
    by the component.
    """

    UNSPECIFIED = (
        electrical_components_pb2.ELECTRICAL_COMPONENT_DIAGNOSTIC_CODE_UNSPECIFIED
    )
    """The error is unspecified (this should not be normally used)."""

    UNKNOWN = electrical_components_pb2.ELECTRICAL_COMPONENT_DIAGNOSTIC_CODE_UNKNOWN
    """The component is reporting an unknown or undefined error.

    This is used when the error can be retrieved from the component but it doesn't match
    any known error.
    """

    SWITCH_ON_FAULT = (
        electrical_components_pb2.ELECTRICAL_COMPONENT_DIAGNOSTIC_CODE_SWITCH_ON_FAULT
    )
    """The component could not be switched on."""

    UNDERVOLTAGE = (
        electrical_components_pb2.ELECTRICAL_COMPONENT_DIAGNOSTIC_CODE_UNDERVOLTAGE
    )
    """The component is operating under the minimum rated voltage."""

    OVERVOLTAGE = (
        electrical_components_pb2.ELECTRICAL_COMPONENT_DIAGNOSTIC_CODE_OVERVOLTAGE
    )
    """The component is operating over the maximum rated voltage."""

    OVERCURRENT = (
        electrical_components_pb2.ELECTRICAL_COMPONENT_DIAGNOSTIC_CODE_OVERCURRENT
    )
    """The component is drawing more current than the maximum rated value."""

    OVERCURRENT_CHARGING = (
        electrical_components_pb2.ELECTRICAL_COMPONENT_DIAGNOSTIC_CODE_OVERCURRENT_CHARGING
    )
    """The component's consumption current is over the maximum rated value during charging."""

    OVERCURRENT_DISCHARGING = (
        electrical_components_pb2.ELECTRICAL_COMPONENT_DIAGNOSTIC_CODE_OVERCURRENT_DISCHARGING
    )
    """The component's production current is over the maximum rated value during discharging."""

    OVERTEMPERATURE = (
        electrical_components_pb2.ELECTRICAL_COMPONENT_DIAGNOSTIC_CODE_OVERTEMPERATURE
    )
    """The component is operating over the maximum rated temperature."""

    UNDERTEMPERATURE = (
        electrical_components_pb2.ELECTRICAL_COMPONENT_DIAGNOSTIC_CODE_UNDERTEMPERATURE
    )
    """The component is operating under the minimum rated temperature."""

    HIGH_HUMIDITY = (
        electrical_components_pb2.ELECTRICAL_COMPONENT_DIAGNOSTIC_CODE_HIGH_HUMIDITY
    )
    """The component is exposed to high humidity levels over the maximum rated value."""

    FUSE_ERROR = (
        electrical_components_pb2.ELECTRICAL_COMPONENT_DIAGNOSTIC_CODE_FUSE_ERROR
    )
    """The component's fuse has blown."""

    PRECHARGE_ERROR = (
        electrical_components_pb2.ELECTRICAL_COMPONENT_DIAGNOSTIC_CODE_PRECHARGE_ERROR
    )
    """The component's precharge unit has failed."""

    PLAUSIBILITY_ERROR = (
        electrical_components_pb2.ELECTRICAL_COMPONENT_DIAGNOSTIC_CODE_PLAUSIBILITY_ERROR
    )
    """Plausibility issues within the system involving this component."""

    FAULT_CURRENT = (
        electrical_components_pb2.ELECTRICAL_COMPONENT_DIAGNOSTIC_CODE_FAULT_CURRENT
    )
    """Fault current detected in the component."""

    SHORT_CIRCUIT = (
        electrical_components_pb2.ELECTRICAL_COMPONENT_DIAGNOSTIC_CODE_SHORT_CIRCUIT
    )
    """Short circuit detected in the component."""

    CONFIG_ERROR = (
        electrical_components_pb2.ELECTRICAL_COMPONENT_DIAGNOSTIC_CODE_CONFIG_ERROR
    )
    """Configuration error related to the component."""

    ILLEGAL_COMPONENT_STATE_CODE_REQUESTED = (
        electrical_components_pb2.ELECTRICAL_COMPONENT_DIAGNOSTIC_CODE_ILLEGAL_COMPONENT_STATE_CODE_REQUESTED  # noqa: E501
    )
    """Illegal state requested for the component."""

    HARDWARE_INACCESSIBLE = (
        electrical_components_pb2.ELECTRICAL_COMPONENT_DIAGNOSTIC_CODE_HARDWARE_INACCESSIBLE
    )
    """Hardware of the component is inaccessible."""

    INTERNAL = electrical_components_pb2.ELECTRICAL_COMPONENT_DIAGNOSTIC_CODE_INTERNAL
    """Internal error within the component."""

    UNAUTHORIZED = (
        electrical_components_pb2.ELECTRICAL_COMPONENT_DIAGNOSTIC_CODE_UNAUTHORIZED
    )
    """The component is unauthorized to perform the last requested action."""

    EXCESS_LEAKAGE_CURRENT = (
        electrical_components_pb2.ELECTRICAL_COMPONENT_DIAGNOSTIC_CODE_EXCESS_LEAKAGE_CURRENT
    )
    """There is excessive leakage current in the component."""

    LOW_SYSTEM_INSULATION_RESISTANCE = (
        electrical_components_pb2.ELECTRICAL_COMPONENT_DIAGNOSTIC_CODE_LOW_SYSTEM_INSULATION_RESISTANCE  # noqa: E501
    )
    """The component is inoperable due to the insulation resistance being too low."""

    GROUND_FAULT = (
        electrical_components_pb2.ELECTRICAL_COMPONENT_DIAGNOSTIC_CODE_GROUND_FAULT
    )
    """The component is inoperable due to the faulty grounding."""

    ARC_FAULT = electrical_components_pb2.ELECTRICAL_COMPONENT_DIAGNOSTIC_CODE_ARC_FAULT
    """The component is inoperable due to arcing."""

    FAN_FAULT = electrical_components_pb2.ELECTRICAL_COMPONENT_DIAGNOSTIC_CODE_FAN_FAULT
    """The component is inoperable due to its fan being faulty."""

    HARDWARE_FAULT = (
        electrical_components_pb2.ELECTRICAL_COMPONENT_DIAGNOSTIC_CODE_HARDWARE_FAULT
    )
    """The component is inoperable due to the component's hardware being faulty."""

    PROTECTIVE_SHUTDOWN = (
        electrical_components_pb2.ELECTRICAL_COMPONENT_DIAGNOSTIC_CODE_PROTECTIVE_SHUTDOWN
    )
    """The component is inoperable due to its hardware being faulty."""

    GRID_OVERVOLTAGE = (
        electrical_components_pb2.ELECTRICAL_COMPONENT_DIAGNOSTIC_CODE_GRID_OVERVOLTAGE
    )
    """The component is inoperable due to the grid voltage being too high."""

    GRID_UNDERVOLTAGE = (
        electrical_components_pb2.ELECTRICAL_COMPONENT_DIAGNOSTIC_CODE_GRID_UNDERVOLTAGE
    )
    """The component is inoperable due to the grid voltage being too low."""

    GRID_OVERFREQUENCY = (
        electrical_components_pb2.ELECTRICAL_COMPONENT_DIAGNOSTIC_CODE_GRID_OVERFREQUENCY
    )
    """The component is inoperable due to the grid frequency being too high."""

    GRID_UNDERFREQUENCY = (
        electrical_components_pb2.ELECTRICAL_COMPONENT_DIAGNOSTIC_CODE_GRID_UNDERFREQUENCY
    )
    """The component is inoperable due to the grid frequency being too low."""

    GRID_DISCONNECTED = (
        electrical_components_pb2.ELECTRICAL_COMPONENT_DIAGNOSTIC_CODE_GRID_DISCONNECTED
    )
    """The component is inoperable due to the grid being disconnected."""

    GRID_VOLTAGE_IMBALANCE = (
        electrical_components_pb2.ELECTRICAL_COMPONENT_DIAGNOSTIC_CODE_GRID_VOLTAGE_IMBALANCE
    )
    """The component is inoperable due to the grid voltage being imbalanced."""

    GRID_ABNORMAL = (
        electrical_components_pb2.ELECTRICAL_COMPONENT_DIAGNOSTIC_CODE_GRID_ABNORMAL
    )
    """The component is inoperable due to the grid being in a non-standard configuration."""

    EV_UNEXPECTED_PILOT_FAILURE = (
        electrical_components_pb2.ELECTRICAL_COMPONENT_DIAGNOSTIC_CODE_EV_UNEXPECTED_PILOT_FAILURE
    )
    """Unexpected pilot failure in an electric vehicle component."""

    EV_CHARGING_CABLE_UNPLUGGED_FROM_STATION = (
        electrical_components_pb2.ELECTRICAL_COMPONENT_DIAGNOSTIC_CODE_EV_CHARGING_CABLE_UNPLUGGED_FROM_STATION  # noqa: E501
    )
    """EV cable was abruptly unplugged from the charging station."""

    EV_CHARGING_CABLE_UNPLUGGED_FROM_EV = (
        electrical_components_pb2.ELECTRICAL_COMPONENT_DIAGNOSTIC_CODE_EV_CHARGING_CABLE_UNPLUGGED_FROM_EV  # noqa: E501
    )
    """EV cable was abruptly unplugged from the vehicle."""

    EV_CHARGING_CABLE_LOCK_FAILED = (
        electrical_components_pb2.ELECTRICAL_COMPONENT_DIAGNOSTIC_CODE_EV_CHARGING_CABLE_LOCK_FAILED
    )
    """EV cable lock failure."""

    EV_CHARGING_CABLE_INVALID = (
        electrical_components_pb2.ELECTRICAL_COMPONENT_DIAGNOSTIC_CODE_EV_CHARGING_CABLE_INVALID
    )
    """Invalid EV cable."""

    EV_CONSUMER_INCOMPATIBLE = (
        electrical_components_pb2.ELECTRICAL_COMPONENT_DIAGNOSTIC_CODE_EV_CONSUMER_INCOMPATIBLE
    )
    """Incompatible EV plug."""

    BATTERY_IMBALANCE = (
        electrical_components_pb2.ELECTRICAL_COMPONENT_DIAGNOSTIC_CODE_BATTERY_IMBALANCE
    )
    """Battery system imbalance."""

    BATTERY_LOW_SOH = (
        electrical_components_pb2.ELECTRICAL_COMPONENT_DIAGNOSTIC_CODE_BATTERY_LOW_SOH
    )
    """Low state of health (SOH) detected in the battery."""

    BATTERY_BLOCK_ERROR = (
        electrical_components_pb2.ELECTRICAL_COMPONENT_DIAGNOSTIC_CODE_BATTERY_BLOCK_ERROR
    )
    """Battery block error."""

    BATTERY_CONTROLLER_ERROR = (
        electrical_components_pb2.ELECTRICAL_COMPONENT_DIAGNOSTIC_CODE_BATTERY_CONTROLLER_ERROR
    )
    """Battery controller error."""

    BATTERY_RELAY_ERROR = (
        electrical_components_pb2.ELECTRICAL_COMPONENT_DIAGNOSTIC_CODE_BATTERY_RELAY_ERROR
    )
    """Battery relay error."""

    BATTERY_CALIBRATION_NEEDED = (
        electrical_components_pb2.ELECTRICAL_COMPONENT_DIAGNOSTIC_CODE_BATTERY_CALIBRATION_NEEDED
    )
    """Battery calibration is needed."""

    RELAY_CYCLE_LIMIT_REACHED = (
        electrical_components_pb2.ELECTRICAL_COMPONENT_DIAGNOSTIC_CODE_RELAY_CYCLE_LIMIT_REACHED
    )
    """Relays have been cycled for the maximum number of times."""

    PV_REVERSAL_POLARITY = (
        electrical_components_pb2.ELECTRICAL_COMPONENT_DIAGNOSTIC_CODE_PV_REVERSAL_POLARITY
    )
    """The PV panels have been connected with reversed polarity."""

    PV_UNDERPERFORMANCE = (
        electrical_components_pb2.ELECTRICAL_COMPONENT_DIAGNOSTIC_CODE_PV_UNDERPERFORMANCE
    )
    """The PV panels are underperforming."""

    PV_FAULT = electrical_components_pb2.ELECTRICAL_COMPONENT_DIAGNOSTIC_CODE_PV_FAULT
    """The PV panels have a fault."""

    PV_REVERSE_CURRENT = (
        electrical_components_pb2.ELECTRICAL_COMPONENT_DIAGNOSTIC_CODE_PV_REVERSE_CURRENT
    )
    """The PV panels are receiving a reverse current."""

    PV_GROUND_FAULT = (
        electrical_components_pb2.ELECTRICAL_COMPONENT_DIAGNOSTIC_CODE_PV_GROUND_FAULT
    )
    """The PV panels are not grounded properly."""

    INVERTER_DC_UNDERVOLTAGE = (
        electrical_components_pb2.ELECTRICAL_COMPONENT_DIAGNOSTIC_CODE_INVERTER_DC_UNDERVOLTAGE
    )
    """The inverter is inoperable due to the DC voltage being too low."""

    INVERTER_DC_OVERVOLTAGE = (
        electrical_components_pb2.ELECTRICAL_COMPONENT_DIAGNOSTIC_CODE_INVERTER_DC_OVERVOLTAGE
    )
    """The inverter is inoperable due to the DC voltage being too high."""


@dataclass(frozen=True, kw_only=True)
class ElectricalComponentDiagnostic:
    """A diagnostic for an electrical component."""

    diagnostic_code: ElectricalComponentDiagnosticCode | int
    """A standardized error code representing the category of the issue.

    Note:
        If the reported error is not known by the client (it could happen when using an
        older version of the client with a newer version of the server), it will be
        represented as an `int` and **not** the
        [`UNKNOWN`][frequenz.client.microgrid.component.ComponentErrorCode.UNKNOWN]
        error (this value is used only when the error is not known by the server).
    """

    vendor_diagnostic_code: str | None = None
    """Vendor-provided error code.

    When available, it reflect manufacturer-defined error identifiers. These codes are
    vendor- and firmware-specific and must be interpreted using the vendor's official
    documentation.
    """

    message: str | None = None
    """Human-readable message providing additional context."""


@dataclass(frozen=True, kw_only=True)
class ElectricalComponentStateSnapshot:
    """A collection of the state, warnings, and errors for a component."""

    origin_time: datetime
    """The time when the state was originally captured."""

    states: frozenset[ElectricalComponentStateCode | int]
    """The set of operational states currently active for the component.

    Note:
        If the reported state is not known by the client (it could happen when using an
        older version of the client with a newer version of the server), it will be
        represented as an `int` and **not** the
        [`UNKNOWN`][frequenz.client.microgrid.component.ElectricalComponentStateCode.UNKNOWN]
        state (this value is used only when the state is not known by the server).

    Note:
        If the state is
        [`ERROR`][frequenz.client.microgrid.component.ElectricalComponentStateCode.ERROR],
        then the electrical component is in an error state. In such cases, the
        [`errors`][frequenz.client.microgrid.component.ElectricalComponentStateSnapshot.errors]
        field will be populated with the list of errors.
    """

    warnings: Sequence[ElectricalComponentDiagnostic]
    """The list of warnings for the component."""

    errors: Sequence[ElectricalComponentDiagnostic]
    """The list of errors for the component.

    This list will only contain errors if the component is in an error state.
    """
