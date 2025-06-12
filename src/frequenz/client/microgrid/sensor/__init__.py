# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Microgrid sensors.

This package provides classes and utilities for working with different types of
sensors in a microgrid environment. [`Sensor`][frequenz.client.microgrid.sensor.Sensor]s
measure various physical metrics in the surrounding environment, such as temperature,
humidity, and solar irradiance.
"""

from ._sensor import Sensor

__all__ = [
    "Sensor",
]
