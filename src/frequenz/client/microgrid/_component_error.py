# License: MIT
# Copyright © 2024 Frequenz Energy-as-a-Service GmbH

"""Common definitions for the microgrid API."""

from dataclasses import dataclass
from enum import Enum
from typing import Self

from frequenz.api.microgrid import battery_pb2, common_pb2, inverter_pb2


class ErrorLevel(Enum):
    """Error level."""

    UNSPECIFIED = common_pb2.ErrorLevel.ERROR_LEVEL_UNSPECIFIED
    """Unspecified component error."""

    WARN = common_pb2.ErrorLevel.ERROR_LEVEL_WARN
    """Action must be taken to prevent a severe error from occurring in the future."""

    CRITICAL = common_pb2.ErrorLevel.ERROR_LEVEL_CRITICAL
    """A severe error that causes the component to fail. Immediate action must be taken."""

    @classmethod
    def from_pb(cls, code: common_pb2.ErrorLevel.ValueType) -> Self:
        """Convert a protobuf error level value to this enum.

        Args:
            code: The protobuf error level to convert.

        Returns:
            The enum value corresponding to the protobuf message.
        """
        try:
            return cls(code)
        except ValueError:
            return cls(cls.UNSPECIFIED)


class BatteryErrorCode(Enum):
    """Battery error code."""

    UNSPECIFIED = battery_pb2.ErrorCode.ERROR_CODE_UNSPECIFIED
    """Unspecified battery error code."""

    HIGH_CURRENT_CHARGE = battery_pb2.ErrorCode.ERROR_CODE_HIGH_CURRENT_CHARGE
    """Charge current is too high."""

    HIGH_CURRENT_DISCHARGE = battery_pb2.ErrorCode.ERROR_CODE_HIGH_CURRENT_DISCHARGE
    """Discharge current is too high."""

    HIGH_VOLTAGE = battery_pb2.ErrorCode.ERROR_CODE_HIGH_VOLTAGE
    """Voltage is too high."""

    LOW_VOLTAGE = battery_pb2.ErrorCode.ERROR_CODE_LOW_VOLTAGE
    """Voltage is too low."""

    HIGH_TEMPERATURE = battery_pb2.ErrorCode.ERROR_CODE_HIGH_TEMPERATURE
    """Temperature is too high."""

    LOW_TEMPERATURE = battery_pb2.ErrorCode.ERROR_CODE_LOW_TEMPERATURE
    """Temperature is too low."""

    HIGH_HUMIDITY = battery_pb2.ErrorCode.ERROR_CODE_HIGH_HUMIDITY
    """Humidity is too high."""

    EXCEEDED_SOP_CHARGE = battery_pb2.ErrorCode.ERROR_CODE_EXCEEDED_SOP_CHARGE
    """Charge current has exceeded component bounds."""

    EXCEEDED_SOP_DISCHARGE = battery_pb2.ErrorCode.ERROR_CODE_EXCEEDED_SOP_DISCHARGE
    """Discharge current has exceeded component bounds."""

    SYSTEM_IMBALANCE = battery_pb2.ErrorCode.ERROR_CODE_SYSTEM_IMBALANCE
    """The battery blocks are not balanced with respect to each other."""

    LOW_SOH = battery_pb2.ErrorCode.ERROR_CODE_LOW_SOH
    """The State of health is low."""

    BLOCK_ERROR = battery_pb2.ErrorCode.ERROR_CODE_BLOCK_ERROR
    """One or more battery blocks have failed."""

    CONTROLLER_ERROR = battery_pb2.ErrorCode.ERROR_CODE_CONTROLLER_ERROR
    """The battery controller has failed."""

    RELAY_ERROR = battery_pb2.ErrorCode.ERROR_CODE_RELAY_ERROR
    """The battery's DC relays have failed."""

    RELAY_CYCLE_LIMIT_REACHED = (
        battery_pb2.ErrorCode.ERROR_CODE_RELAY_CYCLE_LIMIT_REACHED
    )
    """The battery's DC relays have reached the cycles limit in its lifetime specifications."""

    FUSE_ERROR = battery_pb2.ErrorCode.ERROR_CODE_FUSE_ERROR
    """The battery's fuse has failed."""

    EXTERNAL_POWER_SWITCH_ERROR = (
        battery_pb2.ErrorCode.ERROR_CODE_EXTERNAL_POWER_SWITCH_ERROR
    )
    """The eternal power switch has failed."""

    PRECHARGE_ERROR = battery_pb2.ErrorCode.ERROR_CODE_PRECHARGE_ERROR
    """The precharge operation has failed."""

    SYSTEM_PLAUSIBILITY_ERROR = (
        battery_pb2.ErrorCode.ERROR_CODE_SYSTEM_PLAUSIBILITY_ERROR
    )
    """System plausibility checks have failed."""

    SYSTEM_UNDERVOLTAGE_SHUTDOWN = (
        battery_pb2.ErrorCode.ERROR_CODE_SYSTEM_UNDERVOLTAGE_SHUTDOWN
    )
    """System shut down due to extremely low voltage."""

    CALIBRATION_NEEDED = battery_pb2.ErrorCode.ERROR_CODE_CALIBRATION_NEEDED
    """The battery requires a calibration to reset its measurements."""

    @classmethod
    def from_pb(cls, code: battery_pb2.ErrorCode.ValueType) -> Self:
        """Convert a protobuf error code value to this enum.

        Args:
            code: The protobuf error code to convert.

        Returns:
            The enum value corresponding to the protobuf message.
        """
        try:
            return cls(code)
        except ValueError:
            return cls(cls.UNSPECIFIED)


@dataclass(frozen=True, kw_only=True)
class BatteryError:
    """A battery error."""

    code: BatteryErrorCode = BatteryErrorCode.UNSPECIFIED
    """The error code."""

    level: ErrorLevel = ErrorLevel.UNSPECIFIED
    """The error level."""

    message: str = ""
    """The error message."""

    @classmethod
    def from_pb(cls, raw: battery_pb2.Error) -> Self:
        """Create a new instance using a protobuf message to get the values.

        Args:
            raw: The protobuf message to get the values from.

        Returns:
            The new instance with the values from the protobuf message.
        """
        return cls(
            code=BatteryErrorCode.from_pb(raw.code),
            level=ErrorLevel.from_pb(raw.level),
            message=raw.msg,
        )


class InverterErrorCode(Enum):
    """Inverter error code."""

    UNSPECIFIED = inverter_pb2.ErrorCode.ERROR_CODE_UNSPECIFIED
    """Unspecified inverter error code."""

    @classmethod
    def from_pb(cls, code: inverter_pb2.ErrorCode.ValueType) -> Self:
        """Convert a protobuf error code value to this enum.

        Args:
            code: The protobuf error code to convert.

        Returns:
            The enum value corresponding to the protobuf message.
        """
        try:
            return cls(code)
        except ValueError:
            return cls(cls.UNSPECIFIED)


@dataclass(frozen=True, kw_only=True)
class InverterError:
    """An inverter error."""

    code: InverterErrorCode = InverterErrorCode.UNSPECIFIED
    """The error code."""

    level: ErrorLevel = ErrorLevel.UNSPECIFIED
    """The error level."""

    message: str = ""
    """The error message."""

    @classmethod
    def from_pb(cls, raw: inverter_pb2.Error) -> Self:
        """Create a new instance using a protobuf message to get the values.

        Args:
            raw: The protobuf message to get the values from.

        Returns:
            The new instance with the values from the protobuf message.
        """
        return cls(
            code=InverterErrorCode.from_pb(raw.code),
            level=ErrorLevel.from_pb(raw.level),
            message=raw.msg,
        )
