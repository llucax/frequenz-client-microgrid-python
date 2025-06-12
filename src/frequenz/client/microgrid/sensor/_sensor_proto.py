# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Loading of Sensor objects from protobuf messages."""

import logging

from frequenz.api.common.v1.microgrid.sensors import sensors_pb2
from frequenz.client.common.microgrid import MicrogridId
from frequenz.client.common.microgrid.sensors import SensorId

from .._lifetime import Lifetime
from .._lifetime_proto import lifetime_from_proto
from ._sensor import Sensor

_logger = logging.getLogger(__name__)


def sensor_from_proto(message: sensors_pb2.Sensor) -> Sensor:
    """Convert a protobuf message to a `Sensor` instance.

    Args:
        message: The protobuf message.

    Returns:
        The resulting sensor instance.
    """
    major_issues: list[str] = []
    minor_issues: list[str] = []

    sensor = sensor_from_proto_with_issues(
        message, major_issues=major_issues, minor_issues=minor_issues
    )

    if major_issues:
        _logger.warning(
            "Found issues in sensor: %s | Protobuf message:\n%s",
            ", ".join(major_issues),
            message,
        )
    if minor_issues:
        _logger.debug(
            "Found minor issues in sensor: %s | Protobuf message:\n%s",
            ", ".join(minor_issues),
            message,
        )

    return sensor


def sensor_from_proto_with_issues(
    message: sensors_pb2.Sensor,
    *,
    major_issues: list[str],
    minor_issues: list[str],
) -> Sensor:
    """Convert a protobuf message to a sensor instance and collect issues.

    Args:
        message: The protobuf message.
        major_issues: A list to append major issues to.
        minor_issues: A list to append minor issues to.

    Returns:
        The resulting sensor instance.
    """
    sensor_id = SensorId(message.id)
    microgrid = MicrogridId(message.microgrid_id)

    name = message.name or None
    if name is None:
        minor_issues.append("name is empty")

    manufacturer = message.manufacturer or None
    if manufacturer is None:
        minor_issues.append("manufacturer is empty")

    model_name = message.model_name or None
    if model_name is None:
        minor_issues.append("model_name is empty")

    lifetime = _get_operational_lifetime_from_proto(
        message, major_issues=major_issues, minor_issues=minor_issues
    )

    return Sensor(
        id=sensor_id,
        microgrid_id=microgrid,
        name=name,
        manufacturer=manufacturer,
        model_name=model_name,
        operational_lifetime=lifetime,
    )


def _get_operational_lifetime_from_proto(
    message: sensors_pb2.Sensor,
    *,
    major_issues: list[str],
    minor_issues: list[str],
) -> Lifetime:
    """Get the operational lifetime from a protobuf message."""
    if message.HasField("operational_lifetime"):
        try:
            return lifetime_from_proto(message.operational_lifetime)
        except ValueError as exc:
            major_issues.append(
                f"invalid operational lifetime ({exc}), considering it as missing "
                "(i.e. always operational)",
            )
    else:
        minor_issues.append(
            "missing operational lifetime, considering it always operational",
        )
    return Lifetime()
