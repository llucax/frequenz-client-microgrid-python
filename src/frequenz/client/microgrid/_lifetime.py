# License: MIT
# Copyright © 2024 Frequenz Energy-as-a-Service GmbH

"""Lifetime of a microgrid asset."""


from dataclasses import dataclass
from datetime import datetime
from functools import cached_property


@dataclass(frozen=True, kw_only=True)
class Lifetime:
    """An active operational period of a microgrid asset.

    Warning:
        The [`end`][frequenz.client.microgrid.Lifetime.end] timestamp indicates that the
        asset has been permanently removed from the system.
    """

    start: datetime | None = None
    """The moment when the asset became operationally active.

    If `None`, the asset is considered to be active in any past moment previous to the
    [`end`][frequenz.client.microgrid.Lifetime.end].
    """

    end: datetime | None = None
    """The moment when the asset's operational activity ceased.

    If `None`, the asset is considered to be active with no plans to be deactivated.
    """

    def __post_init__(self) -> None:
        """Validate this lifetime."""
        if self.start is not None and self.end is not None and self.start > self.end:
            raise ValueError("Start must be before or equal to end.")

    @cached_property
    def active(self) -> bool:
        """Whether this lifetime is currently active."""
        now = datetime.now()
        if self.start is not None and self.start > now:
            return False
        return self.end is None or self.end >= now
