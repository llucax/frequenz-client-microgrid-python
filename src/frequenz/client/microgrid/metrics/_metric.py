# License: MIT
# Copyright © 2024 Frequenz Energy-as-a-Service GmbH

"""Supported metrics for microgrid components."""


import enum


@enum.unique
class Metric(enum.Enum):
    """List of supported metrics.

    Note: AC energy metrics information
        - This energy metric is reported directly from the component, and not a
          result of aggregations in our systems. If a component does not have this
          metric, this field cannot be populated.

        - Components that provide energy metrics reset this metric from time to
          time. This behaviour is specific to each component model. E.g., some
          components reset it on UTC 00:00:00.

        - This energy metric does not specify the timestamp since when the energy
          was being accumulated, and therefore can be inconsistent.
    """

    UNSPECIFIED = 0
    """The metric is unspecified (this should not be used)."""

    DC_VOLTAGE = 1
    """The direct current voltage."""

    DC_CURRENT = 2
    """The direct current current."""

    DC_POWER = 3
    """The direct current power."""

    AC_FREQUENCY = 10
    """The alternating current frequency."""

    AC_VOLTAGE = 11
    """The alternating current electric potential difference."""

    AC_VOLTAGE_PHASE_1_N = 12
    """The alternating current electric potential difference between phase 1 and neutral."""

    AC_VOLTAGE_PHASE_2_N = 13
    """The alternating current electric potential difference between phase 2 and neutral."""

    AC_VOLTAGE_PHASE_3_N = 14
    """The alternating current electric potential difference between phase 3 and neutral."""

    AC_VOLTAGE_PHASE_1_PHASE_2 = 15
    """The alternating current electric potential difference between phase 1 and phase 2."""

    AC_VOLTAGE_PHASE_2_PHASE_3 = 16
    """The alternating current electric potential difference between phase 2 and phase 3."""

    AC_VOLTAGE_PHASE_3_PHASE_1 = 17
    """The alternating current electric potential difference between phase 3 and phase 1."""

    AC_CURRENT = 18
    """The alternating current current."""

    AC_CURRENT_PHASE_1 = 19
    """The alternating current current in phase 1."""

    AC_CURRENT_PHASE_2 = 20
    """The alternating current current in phase 2."""

    AC_CURRENT_PHASE_3 = 21
    """The alternating current current in phase 3."""

    AC_APPARENT_POWER = 22
    """The alternating current apparent power."""

    AC_APPARENT_POWER_PHASE_1 = 23
    """The alternating current apparent power in phase 1."""

    AC_APPARENT_POWER_PHASE_2 = 24
    """The alternating current apparent power in phase 2."""

    AC_APPARENT_POWER_PHASE_3 = 25
    """The alternating current apparent power in phase 3."""

    AC_ACTIVE_POWER = 26
    """The alternating current active power."""

    AC_ACTIVE_POWER_PHASE_1 = 27
    """The alternating current active power in phase 1."""

    AC_ACTIVE_POWER_PHASE_2 = 28
    """The alternating current active power in phase 2."""

    AC_ACTIVE_POWER_PHASE_3 = 29
    """The alternating current active power in phase 3."""

    AC_REACTIVE_POWER = 30
    """The alternating current reactive power."""

    AC_REACTIVE_POWER_PHASE_1 = 31
    """The alternating current reactive power in phase 1."""

    AC_REACTIVE_POWER_PHASE_2 = 32
    """The alternating current reactive power in phase 2."""

    AC_REACTIVE_POWER_PHASE_3 = 33
    """The alternating current reactive power in phase 3."""

    AC_POWER_FACTOR = 40
    """The alternating current power factor."""

    AC_POWER_FACTOR_PHASE_1 = 41
    """The alternating current power factor in phase 1."""

    AC_POWER_FACTOR_PHASE_2 = 42
    """The alternating current power factor in phase 2."""

    AC_POWER_FACTOR_PHASE_3 = 43
    """The alternating current power factor in phase 3."""

    AC_APPARENT_ENERGY = 50
    """The alternating current apparent energy."""

    AC_APPARENT_ENERGY_PHASE_1 = 51
    """The alternating current apparent energy in phase 1."""

    AC_APPARENT_ENERGY_PHASE_2 = 52
    """The alternating current apparent energy in phase 2."""

    AC_APPARENT_ENERGY_PHASE_3 = 53
    """The alternating current apparent energy in phase 3."""

    AC_ACTIVE_ENERGY = 54
    """The alternating current active energy."""

    AC_ACTIVE_ENERGY_PHASE_1 = 55
    """The alternating current active energy in phase 1."""

    AC_ACTIVE_ENERGY_PHASE_2 = 56
    """The alternating current active energy in phase 2."""

    AC_ACTIVE_ENERGY_PHASE_3 = 57
    """The alternating current active energy in phase 3."""

    AC_ACTIVE_ENERGY_CONSUMED = 58
    """The alternating current active energy consumed."""

    AC_ACTIVE_ENERGY_CONSUMED_PHASE_1 = 59
    """The alternating current active energy consumed in phase 1."""

    AC_ACTIVE_ENERGY_CONSUMED_PHASE_2 = 60
    """The alternating current active energy consumed in phase 2."""

    AC_ACTIVE_ENERGY_CONSUMED_PHASE_3 = 61
    """The alternating current active energy consumed in phase 3."""

    AC_ACTIVE_ENERGY_DELIVERED = 62
    """The alternating current active energy delivered."""

    AC_ACTIVE_ENERGY_DELIVERED_PHASE_1 = 63
    """The alternating current active energy delivered in phase 1."""

    AC_ACTIVE_ENERGY_DELIVERED_PHASE_2 = 64
    """The alternating current active energy delivered in phase 2."""

    AC_ACTIVE_ENERGY_DELIVERED_PHASE_3 = 65
    """The alternating current active energy delivered in phase 3."""

    AC_REACTIVE_ENERGY = 66
    """The alternating current reactive energy."""

    AC_REACTIVE_ENERGY_PHASE_1 = 67
    """The alternating current reactive energy in phase 1."""

    C_REACTIVE_ENERGY_PHASE_2 = 69
    """The alternating current reactive energy in phase 2."""

    AC_REACTIVE_ENERGY_PHASE_3 = 70
    """The alternating current reactive energy in phase 3."""

    AC_TOTAL_HARMONIC_DISTORTION_CURRENT = 80
    """The alternating current total harmonic distortion current."""

    AC_TOTAL_HARMONIC_DISTORTION_CURRENT_PHASE_1 = 81
    """The alternating current total harmonic distortion current in phase 1."""

    AC_TOTAL_HARMONIC_DISTORTION_CURRENT_PHASE_2 = 82
    """The alternating current total harmonic distortion current in phase 2."""

    AC_TOTAL_HARMONIC_DISTORTION_CURRENT_PHASE_3 = 83
    """The alternating current total harmonic distortion current in phase 3."""

    BATTERY_CAPACITY = 101
    """The capacity of the battery."""

    BATTERY_SOC_PCT = 102
    """The state of charge of the battery as a percentage."""

    BATTERY_TEMPERATURE = 103
    """The temperature of the battery."""

    INVERTER_TEMPERATURE = 120
    """The temperature of the inverter."""

    INVERTER_TEMPERATURE_CABINET = 121
    """The temperature of the inverter cabinet."""

    INVERTER_TEMPERATURE_HEATSINK = 122
    """The temperature of the inverter heatsink."""

    INVERTER_TEMPERATURE_TRANSFORMER = 123
    """The temperature of the inverter transformer."""

    EV_CHARGER_TEMPERATURE = 140
    """The temperature of the EV charger."""

    SENSOR_WIND_SPEED = 160
    """The speed of the wind measured."""

    SENSOR_WIND_DIRECTION = 162
    """The direction of the wind measured."""

    SENSOR_TEMPERATURE = 163
    """The temperature measured."""

    SENSOR_RELATIVE_HUMIDITY = 164
    """The relative humidity measured."""

    SENSOR_DEW_POINT = 165
    """The dew point measured."""

    SENSOR_AIR_PRESSURE = 166
    """The air pressure measured."""

    SENSOR_IRRADIANCE = 167
    """The irradiance measured."""
