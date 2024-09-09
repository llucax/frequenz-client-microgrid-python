# License: MIT
# Copyright © 2024 Frequenz Energy-as-a-Service GmbH

"""Unknown component."""

import dataclasses
from typing import Any, Literal, Self, TypeAlias

from ._base import Component
from ._category import ComponentCategory


@dataclasses.dataclass(frozen=True, kw_only=True)
class ProblematicComponent(Component):
    """An abstract component with a problem."""

    category_specific_metadata: dict[str, Any] = dataclasses.field(default_factory=dict)
    """The category specific metadata of this component."""

    # pylint: disable-next=unused-argument
    def __new__(cls, *args: Any, **kwargs: Any) -> Self:
        """Prevent instantiation of this class."""
        if cls is ProblematicComponent:
            raise TypeError(f"Cannot instantiate {cls.__name__} directly")
        return super().__new__(cls)


@dataclasses.dataclass(frozen=True, kw_only=True)
class UnspecifiedComponent(ProblematicComponent):
    """A component of unspecified type."""

    category: Literal[ComponentCategory.UNSPECIFIED] = ComponentCategory.UNSPECIFIED
    """The category of this component."""


@dataclasses.dataclass(frozen=True, kw_only=True)
class UnrecognizedComponent(ProblematicComponent):
    """A component of an unrecognized type."""

    category: int
    """The category of this component."""


@dataclasses.dataclass(frozen=True, kw_only=True)
class MismatchedCategoryComponent(ProblematicComponent):
    """A component with a mismatch in the category.

    This component declared a category but carries category specific metadata that
    doesn't match the declared category.
    """

    category: ComponentCategory | int
    """The category of this component."""


ProblematicComponentTypes: TypeAlias = (
    MismatchedCategoryComponent | UnrecognizedComponent | UnspecifiedComponent
)
"""All possible component types that has a problem."""
