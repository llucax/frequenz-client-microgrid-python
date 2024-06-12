# License: MIT
# Copyright © 2024 Frequenz Energy-as-a-Service GmbH

"""Metadata that describes a microgrid."""


class EnterpriseId:
    """A unique identifier for an enterprise account."""

    def __init__(self, id_: int, /) -> None:
        """Initialize this instance.

        Args:
            id_: The numeric unique identifier of the enterprise account.

        Raises:
            ValueError: If the ID is negative.
        """
        if id_ < 0:
            raise ValueError("Enterprise ID can't be negative.")
        self._id = id_

    def __int__(self) -> int:
        """Return the numeric ID of this instance."""
        return self._id

    def __eq__(self, other: object) -> bool:
        """Check if this instance is equal to another object."""
        # This is not an unidiomatic typecheck, that's an odd name for the check.
        # isinstance() returns True for subclasses, which is not what we want here.
        # pylint: disable-next=unidiomatic-typecheck
        return type(other) is EnterpriseId and self._id == other._id

    def __hash__(self) -> int:
        """Return the hash of this instance."""
        # We include the class because we explicitly want to avoid the same ID to give
        # the same hash for different classes of IDs
        return hash((EnterpriseId, self._id))

    def __repr__(self) -> str:
        """Return the string representation of this instance."""
        return f"{type(self).__name__}({self._id!r})"

    def __str__(self) -> str:
        """Return the short string representation of this instance."""
        return f"EID{self._id}"


class MicrogridId:
    """A unique identifier for a microgrid."""

    def __init__(self, id_: int, /) -> None:
        """Initialize this instance.

        Args:
            id_: The numeric unique identifier of the microgrid.

        Raises:
            ValueError: If the ID is negative.
        """
        if id_ < 0:
            raise ValueError("Microgrid ID can't be negative.")
        self._id = id_

    def __int__(self) -> int:
        """Return the numeric ID of this instance."""
        return self._id

    def __eq__(self, other: object) -> bool:
        """Check if this instance is equal to another object."""
        # This is not an unidiomatic typecheck, that's an odd name for the check.
        # isinstance() returns True for subclasses, which is not what we want here.
        # pylint: disable-next=unidiomatic-typecheck
        return type(other) is MicrogridId and self._id == other._id

    def __hash__(self) -> int:
        """Return the hash of this instance."""
        # We include the class because we explicitly want to avoid the same ID to give
        # the same hash for different classes of IDs
        return hash((MicrogridId, self._id))

    def __repr__(self) -> str:
        """Return the string representation of this instance."""
        return f"{type(self).__name__}({self._id!r})"

    def __str__(self) -> str:
        """Return the short string representation of this instance."""
        return f"MID{self._id}"
