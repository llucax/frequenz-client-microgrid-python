# License: MIT
# Copyright © 2024 Frequenz Energy-as-a-Service GmbH

"""Base component from which all other components inherit."""

import dataclasses
import logging
from collections.abc import Mapping
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

    category: ComponentCategory | int
    """The category of this component.

    Note:
        This should not be used normally, you should test if a component
        [`isinstance`][] of a concrete component class instead.

        It is only provided for using with a newer version of the API where the client
        doesn't know about a new category yet (i.e. for use with
        [`UnrecognizedComponent`][frequenz.client.microgrid.component.UnrecognizedComponent])
        and in case some low level code needs to know the category of a component.
        """

    status: ComponentStatus | int = ComponentStatus.ACTIVE
    """The status of this component.

    Note:
        This should not be used normally, you should test if a component is active
        by checking the [`active`][frequenz.client.microgrid.component.Component.active]
        property instead.
    """

    name: str | None = None
    """The name of this component."""

    manufacturer: str | None = None
    """The manufacturer of this component."""

    model_name: str | None = None
    """The model name of this component."""

    operational_lifetime: Lifetime = dataclasses.field(default_factory=Lifetime)
    """The operational lifetime of this component."""

    rated_bounds: Mapping[Metric | int, Bounds] = dataclasses.field(
        default_factory=dict,
        # dict is not hashable, so we don't use this field to calculate the hash. This
        # shouldn't be a problem since it is very unlikely that two components with all
        # other attributes being equal would have different category specific metadata,
        # so hash collisions should be still very unlikely.
        # TODO: Test hashing components
        hash=False,
    )
    """List of rated bounds present for the component identified by Metric."""

    category_specific_metadata: Mapping[str, Any] = dataclasses.field(
        default_factory=dict,
        # dict is not hashable, so we don't use this field to calculate the hash. This
        # shouldn't be a problem since it is very unlikely that two components with all
        # other attributes being equal would have different category specific metadata,
        # so hash collisions should be still very unlikely.
        hash=False,
    )
    """The category specific metadata of this component.

    Note:
        This should not be used normally, it is only useful when accessing a newer
        version of the API where the client doesn't know about the new metadata fields
        yet (i.e. for use with
        [`UnrecognizedComponent`][frequenz.client.microgrid.component.UnrecognizedComponent]).
    """

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
