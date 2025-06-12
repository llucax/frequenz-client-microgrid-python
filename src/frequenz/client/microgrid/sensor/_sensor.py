# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Microgrid sensors."""

import dataclasses
from datetime import datetime, timezone

from frequenz.client.common.microgrid import MicrogridId
from frequenz.client.common.microgrid.sensors import SensorId

from .._lifetime import Lifetime


@dataclasses.dataclass(frozen=True, kw_only=True)
class Sensor:
    """Measures environmental metrics in the microgrid."""

    id: SensorId
    """This sensor's ID."""

    microgrid_id: MicrogridId
    """The ID of the microgrid this sensor belongs to."""

    name: str | None = None
    """The name of this sensor."""

    manufacturer: str | None = None
    """The manufacturer of this sensor."""

    model_name: str | None = None
    """The model name of this sensor."""

    operational_lifetime: Lifetime = dataclasses.field(default_factory=Lifetime)
    """The operational lifetime of this sensor."""

    @property
    def identity(self) -> tuple[SensorId, MicrogridId]:
        """The identity of this sensor.

        This uses the sensor ID and microgrid ID to identify a sensor without
        considering the other attributes, so even if a sensor state changed, the
        identity remains the same.
        """
        return (self.id, self.microgrid_id)

    def is_operational_at(self, timestamp: datetime) -> bool:
        """Check whether this sensor is operational at a specific timestamp."""
        return self.operational_lifetime.is_operational_at(timestamp)

    def is_operational_now(self) -> bool:
        """Whether this sensor is currently operational."""
        return self.is_operational_at(datetime.now(timezone.utc))

    def __str__(self) -> str:
        """Return a human-readable string representation of this instance."""
        name = f":{self.name}" if self.name else ""
        return f"<{type(self).__name__}:{self.id}{name}>"
