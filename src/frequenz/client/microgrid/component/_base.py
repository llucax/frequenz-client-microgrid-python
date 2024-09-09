# License: MIT
# Copyright © 2024 Frequenz Energy-as-a-Service GmbH

"""Base component from which all other components inherit."""

import dataclasses
import logging
from functools import cached_property
from typing import Any, Self

from .._id import ComponentId, MicrogridId
from .._lifetime import Lifetime
from ..metrics._bounds import Bounds
from ..metrics._metric import Metric
from ._category import ComponentCategory
from ._status import ComponentStatus

_logger = logging.getLogger(__name__)


@dataclasses.dataclass(frozen=True, kw_only=True)
class Component:  # pylint: disable=too-many-instance-attributes
    """A base class for all components."""

    id: ComponentId
    """This component's ID."""

    microgrid_id: MicrogridId
    """The ID of the microgrid this component belongs to."""

    name: str | None
    """The name of this component."""

    category: ComponentCategory | int
    """The category of this component."""

    manufacturer: str | None
    """The manufacturer of this component."""

    model_name: str | None
    """The model name of this component."""

    status: ComponentStatus | int
    """The status of this component."""

    operational_lifetime: Lifetime
    """The operational lifetime of this component."""

    rated_bounds: dict[Metric | int, Bounds]
    """List of rated bounds present for the component identified by Metric."""

    # pylint: disable-next=unused-argument
    def __new__(cls, *args: Any, **kwargs: Any) -> Self:
        """Prevent instantiation of this class."""
        if cls is Component:
            raise TypeError(f"Cannot instantiate {cls.__name__} directly")
        return super().__new__(cls)

    @cached_property
    def active(self) -> bool:
        """Whether this component is currently active."""
        if self.status is ComponentStatus.UNSPECIFIED:
            # Because this is a cached property, the warning will only be logged once.
            _logger.warning(
                "Component %s has an unspecified status. Assuming it is active.",
                self,
            )
        return self.status in (ComponentStatus.ACTIVE, ComponentStatus.UNSPECIFIED)

    def __str__(self) -> str:
        """Return a human-readable string representation of this instance."""
        name = f":{self.name}" if self.name else ""
        return f"{self.id}<{type(self).__name__}>{name}"
