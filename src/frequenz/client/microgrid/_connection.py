# License: MIT
# Copyright © 2022 Frequenz Energy-as-a-Service GmbH

"""Defines the connections between microgrid components."""


from dataclasses import dataclass


@dataclass(frozen=True)
class Connection:
    """Metadata for a connection between microgrid components."""

    start: int
    """The component ID that represents the start component of the connection."""

    end: int
    """The component ID that represents the end component of the connection."""

    def is_valid(self) -> bool:
        """Check if this instance contains valid data.

        Returns:
            `True` if `start >= 0`, `end > 0`, and `start != end`, `False`
                otherwise.
        """
        return self.start >= 0 and self.end > 0 and self.start != self.end
