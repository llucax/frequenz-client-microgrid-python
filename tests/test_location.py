# License: MIT
# Copyright © 2024 Frequenz Energy-as-a-Service GmbH

"""Tests for the microgrid metadata types."""

from typing import Iterator
from unittest.mock import MagicMock, patch
from zoneinfo import ZoneInfo

import pytest

from frequenz.client.microgrid import Location


@pytest.fixture
def timezone_finder() -> Iterator[MagicMock]:
    """Return a mock timezone finder."""
    with patch(
        "frequenz.client.microgrid._location._timezone_finder", autospec=True
    ) as mock_timezone_finder:
        yield mock_timezone_finder


def test_location_timezone_constructor() -> None:
    """Test the location timezone is not looked up if it is not used."""
    location = Location(latitude=52.52, longitude=13.405, country_code="DE")

    assert location.latitude == 52.52
    assert location.longitude == 13.405
    assert location.country_code == "DE"


def test_location_timezone_not_looked_up_if_unused(timezone_finder: MagicMock) -> None:
    """Test the location timezone is not looked up if it is not used."""
    _ = Location(latitude=52.52, longitude=13.405, country_code="DE")
    timezone_finder.timezone_at.assert_not_called()


def test_location_timezone_looked_up_but_not_found(timezone_finder: MagicMock) -> None:
    """Test the location timezone is not looked up if it is not used."""
    timezone_finder.timezone_at.return_value = None

    location = Location(latitude=52.52, longitude=13.405, country_code="DE")

    assert location.timezone is None
    timezone_finder.timezone_at.assert_called_once_with(lat=52.52, lng=13.405)


def test_location_timezone_looked_up_and_found(timezone_finder: MagicMock) -> None:
    """Test the location timezone is not looked up if it is not used."""
    timezone_finder.timezone_at.return_value = "Europe/Berlin"

    location = Location(latitude=52.52, longitude=13.405, country_code="DE")

    assert location.timezone == ZoneInfo(key="Europe/Berlin")
    timezone_finder.timezone_at.assert_called_once_with(lat=52.52, lng=13.405)
