# License: MIT
# Copyright © 2024 Frequenz Energy-as-a-Service GmbH

"""Loading of ComponentConnection objects from protobuf messages."""

import logging

from frequenz.api.common.v1.microgrid.components import components_pb2

from .._id import ComponentId
from .._lifetime import Lifetime
from .._lifetime_proto import lifetime_from_proto
from ._connection import ComponentConnection

_logger = logging.getLogger(__name__)


def component_connection_from_proto(
    message: components_pb2.ComponentConnection,
) -> ComponentConnection:
    """Create a `ComponentConnection` from a protobuf message."""
    major_issues: list[str] = []
    minor_issues: list[str] = []

    source_component_id = ComponentId(message.source_component_id)
    destination_component_id = ComponentId(message.destination_component_id)
    if source_component_id == destination_component_id:
        major_issues.append(
            f"source and destination are the same: {source_component_id}",
        )

    lifetime = _get_operational_lifetime_from_proto(
        message, major_issues=major_issues, minor_issues=minor_issues
    )

    if major_issues:
        _logger.warning(
            "Found issues in component connection: %s | Protobuf message:\n%s",
            ", ".join(major_issues),
            message,
        )
    if minor_issues:
        _logger.debug(
            "Found minor issues in component connection: %s | Protobuf message:\n%s",
            ", ".join(minor_issues),
            message,
        )

    return ComponentConnection(
        source=source_component_id,
        destination=destination_component_id,
        operational_lifetime=lifetime,
    )


def _get_operational_lifetime_from_proto(
    message: components_pb2.ComponentConnection,
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
