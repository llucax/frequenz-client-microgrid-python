# License: MIT
# Copyright © 2022 Frequenz Energy-as-a-Service GmbH

"""Tests for the microgrid Connection type."""

from frequenz.client.microgrid import Connection


# pylint: disable=invalid-name
def test_Connection() -> None:
    """Test the microgrid Connection type."""
    c00 = Connection(0, 0)
    assert not c00.is_valid()

    c01 = Connection(0, 1)
    assert c01.is_valid()

    c10 = Connection(1, 0)
    assert not c10.is_valid()

    c11 = Connection(1, 1)
    assert not c11.is_valid()

    c12 = Connection(1, 2)
    assert c12.is_valid()

    c21 = Connection(2, 1)
    assert c21.is_valid()
