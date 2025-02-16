# License: MIT
# Copyright © 2022 Frequenz Energy-as-a-Service GmbH

"""Component data types for data coming from a microgrid."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Self

from frequenz.microgrid.betterproto.frequenz.api import microgrid

from ._component_error import BatteryError, InverterError
from ._component_states import (
    BatteryComponentState,
    BatteryRelayState,
    EVChargerCableState,
    EVChargerComponentState,
    InverterComponentState,
)


@dataclass(frozen=True)
class ComponentData(ABC):
    """A private base class for strongly typed component data classes."""

    component_id: int
    """The ID identifying this component in the microgrid."""

    timestamp: datetime
    """The timestamp of when the data was measured."""

    # The `raw` attribute is excluded from the constructor as it can only be provided
    # when instantiating `ComponentData` using the `from_proto` method, which reads
    # data from a protobuf message. The whole protobuf message is stored as the `raw`
    # attribute. When `ComponentData` is not instantiated from a protobuf message,
    # i.e. using the constructor, `raw` will be set to `None`.
    raw: microgrid.ComponentData | None = field(default=None, init=False)
    """Raw component data as decoded from the wire."""

    def _set_raw(self, raw: microgrid.ComponentData) -> None:
        """Store raw protobuf message.

        It is preferred to keep the dataclasses immutable (frozen) and make the `raw`
            attribute read-only, which is why the approach of writing to `__dict__`
            was used, instead of mutating the `self.raw = raw` attribute directly.

        Args:
            raw: raw component data as decoded from the wire.
        """
        self.__dict__["raw"] = raw

    @classmethod
    @abstractmethod
    def from_proto(cls, raw: microgrid.ComponentData) -> Self:
        """Create ComponentData from a protobuf message.

        Args:
            raw: raw component data as decoded from the wire.

        Returns:
            The instance created from the protobuf message.
        """


@dataclass(frozen=True)
class MeterData(ComponentData):
    """A wrapper class for holding meter data."""

    active_power: float
    """The total active 3-phase AC power, in Watts (W).

    Represented in the passive sign convention.

    * Positive means consumption from the grid.
    * Negative means supply into the grid.
    """

    active_power_per_phase: tuple[float, float, float]
    """The per-phase AC active power for phase 1, 2, and 3 respectively, in Watt (W).

    Represented in the passive sign convention.

    * Positive means consumption from the grid.
    * Negative means supply into the grid.
    """

    reactive_power: float
    """The total reactive 3-phase AC power, in Volt-Ampere Reactive (VAr).

    * Positive power means capacitive (current leading w.r.t. voltage).
    * Negative power means inductive (current lagging w.r.t. voltage).
    """

    reactive_power_per_phase: tuple[float, float, float]
    """The per-phase AC reactive power, in Volt-Ampere Reactive (VAr).

    The provided values are for phase 1, 2, and 3 respectively.

    * Positive power means capacitive (current leading w.r.t. voltage).
    * Negative power means inductive (current lagging w.r.t. voltage).
    """

    current_per_phase: tuple[float, float, float]
    """AC current in Amperes (A) for phase/line 1,2 and 3 respectively.

    Represented in the passive sign convention.

    * Positive means consumption from the grid.
    * Negative means supply into the grid.
    """

    voltage_per_phase: tuple[float, float, float]
    """The ac voltage in volts (v) between the line and the neutral wire for phase/line
        1,2 and 3 respectively.
    """

    frequency: float
    """The AC power frequency in Hertz (Hz)."""

    @classmethod
    def from_proto(cls, raw: microgrid.ComponentData) -> Self:
        """Create MeterData from a protobuf message.

        Args:
            raw: raw component data as decoded from the wire.

        Returns:
            Instance of MeterData created from the protobuf message.
        """
        meter_data = cls(
            component_id=raw.id,
            timestamp=raw.ts,
            active_power=raw.meter.data.ac.power_active.value,
            active_power_per_phase=(
                raw.meter.data.ac.phase_1.power_active.value,
                raw.meter.data.ac.phase_2.power_active.value,
                raw.meter.data.ac.phase_3.power_active.value,
            ),
            reactive_power=raw.meter.data.ac.power_reactive.value,
            reactive_power_per_phase=(
                raw.meter.data.ac.phase_1.power_reactive.value,
                raw.meter.data.ac.phase_2.power_reactive.value,
                raw.meter.data.ac.phase_3.power_reactive.value,
            ),
            current_per_phase=(
                raw.meter.data.ac.phase_1.current.value,
                raw.meter.data.ac.phase_2.current.value,
                raw.meter.data.ac.phase_3.current.value,
            ),
            voltage_per_phase=(
                raw.meter.data.ac.phase_1.voltage.value,
                raw.meter.data.ac.phase_2.voltage.value,
                raw.meter.data.ac.phase_3.voltage.value,
            ),
            frequency=raw.meter.data.ac.frequency.value,
        )
        meter_data._set_raw(raw=raw)
        return meter_data


@dataclass(frozen=True)
class BatteryData(ComponentData):  # pylint: disable=too-many-instance-attributes
    """A wrapper class for holding battery data."""

    soc: float
    """Battery's overall SoC in percent (%)."""

    soc_lower_bound: float
    """The SoC below which discharge commands will be blocked by the system,
        in percent (%).
    """

    soc_upper_bound: float
    """The SoC above which charge commands will be blocked by the system,
        in percent (%).
    """

    capacity: float
    """The capacity of the battery in Wh (Watt-hour)."""

    power_inclusion_lower_bound: float
    """Lower inclusion bound for battery power in watts.

    This is the lower limit of the range within which power requests are allowed for the
    battery.

    See [`frequenz.api.common.metrics_pb2.Metric.system_inclusion_bounds`][] and
    [`frequenz.api.common.metrics_pb2.Metric.system_exclusion_bounds`][] for more
    details.
    """

    power_exclusion_lower_bound: float
    """Lower exclusion bound for battery power in watts.

    This is the lower limit of the range within which power requests are not allowed for
    the battery.

    See [`frequenz.api.common.metrics_pb2.Metric.system_inclusion_bounds`][] and
    [`frequenz.api.common.metrics_pb2.Metric.system_exclusion_bounds`][] for more
    details.
    """

    power_inclusion_upper_bound: float
    """Upper inclusion bound for battery power in watts.

    This is the upper limit of the range within which power requests are allowed for the
    battery.

    See [`frequenz.api.common.metrics_pb2.Metric.system_inclusion_bounds`][] and
    [`frequenz.api.common.metrics_pb2.Metric.system_exclusion_bounds`][] for more
    details.
    """

    power_exclusion_upper_bound: float
    """Upper exclusion bound for battery power in watts.

    This is the upper limit of the range within which power requests are not allowed for
    the battery.

    See [`frequenz.api.common.metrics_pb2.Metric.system_inclusion_bounds`][] and
    [`frequenz.api.common.metrics_pb2.Metric.system_exclusion_bounds`][] for more
    details.
    """

    temperature: float
    """The (average) temperature reported by the battery, in Celsius (°C)."""

    relay_state: BatteryRelayState
    """State of the battery relay."""

    component_state: BatteryComponentState
    """State of the battery."""

    errors: list[BatteryError]
    """List of errors in protobuf struct."""

    @classmethod
    def from_proto(cls, raw: microgrid.ComponentData) -> Self:
        """Create BatteryData from a protobuf message.

        Args:
            raw: raw component data as decoded from the wire.

        Returns:
            Instance of BatteryData created from the protobuf message.
        """
        raw_power = raw.battery.data.dc.power
        battery_data = cls(
            component_id=raw.id,
            timestamp=raw.ts,
            soc=raw.battery.data.soc.avg,
            soc_lower_bound=raw.battery.data.soc.system_inclusion_bounds.lower,
            soc_upper_bound=raw.battery.data.soc.system_inclusion_bounds.upper,
            capacity=raw.battery.properties.capacity,
            power_inclusion_lower_bound=raw_power.system_inclusion_bounds.lower,
            power_exclusion_lower_bound=raw_power.system_exclusion_bounds.lower,
            power_inclusion_upper_bound=raw_power.system_inclusion_bounds.upper,
            power_exclusion_upper_bound=raw_power.system_exclusion_bounds.upper,
            temperature=raw.battery.data.temperature.avg,
            relay_state=BatteryRelayState.from_pb(raw.battery.state.relay_state),
            component_state=BatteryComponentState.from_pb(
                raw.battery.state.component_state
            ),
            errors=[BatteryError.from_pb(e) for e in raw.battery.errors],
        )
        battery_data._set_raw(raw=raw)
        return battery_data


@dataclass(frozen=True)
class InverterData(ComponentData):  # pylint: disable=too-many-instance-attributes
    """A wrapper class for holding inverter data."""

    active_power: float
    """The total active 3-phase AC power, in Watts (W).

    Represented in the passive sign convention.

    * Positive means consumption from the grid.
    * Negative means supply into the grid.
    """

    active_power_per_phase: tuple[float, float, float]
    """The per-phase AC active power for phase 1, 2, and 3 respectively, in Watt (W).

    Represented in the passive sign convention.

    * Positive means consumption from the grid.
    * Negative means supply into the grid.
    """

    reactive_power: float
    """The total reactive 3-phase AC power, in Volt-Ampere Reactive (VAr).

    * Positive power means capacitive (current leading w.r.t. voltage).
    * Negative power means inductive (current lagging w.r.t. voltage).
    """

    reactive_power_per_phase: tuple[float, float, float]
    """The per-phase AC reactive power, in Volt-Ampere Reactive (VAr).

    The provided values are for phase 1, 2, and 3 respectively.

    * Positive power means capacitive (current leading w.r.t. voltage).
    * Negative power means inductive (current lagging w.r.t. voltage).
    """

    current_per_phase: tuple[float, float, float]
    """AC current in Amperes (A) for phase/line 1, 2 and 3 respectively.

    Represented in the passive sign convention.

    * Positive means consumption from the grid.
    * Negative means supply into the grid.
    """

    voltage_per_phase: tuple[float, float, float]
    """The AC voltage in Volts (V) between the line and the neutral wire for
       phase/line 1, 2 and 3 respectively.
    """

    active_power_inclusion_lower_bound: float
    """Lower inclusion bound for inverter power in watts.

    This is the lower limit of the range within which power requests are allowed for the
    inverter.

    See [`frequenz.api.common.metrics_pb2.Metric.system_inclusion_bounds`][] and
    [`frequenz.api.common.metrics_pb2.Metric.system_exclusion_bounds`][] for more
    details.
    """

    active_power_exclusion_lower_bound: float
    """Lower exclusion bound for inverter power in watts.

    This is the lower limit of the range within which power requests are not allowed for
    the inverter.

    See [`frequenz.api.common.metrics_pb2.Metric.system_inclusion_bounds`][] and
    [`frequenz.api.common.metrics_pb2.Metric.system_exclusion_bounds`][] for more
    details.
    """

    active_power_inclusion_upper_bound: float
    """Upper inclusion bound for inverter power in watts.

    This is the upper limit of the range within which power requests are allowed for the
    inverter.

    See [`frequenz.api.common.metrics_pb2.Metric.system_inclusion_bounds`][] and
    [`frequenz.api.common.metrics_pb2.Metric.system_exclusion_bounds`][] for more
    details.
    """

    active_power_exclusion_upper_bound: float
    """Upper exclusion bound for inverter power in watts.

    This is the upper limit of the range within which power requests are not allowed for
    the inverter.

    See [`frequenz.api.common.metrics_pb2.Metric.system_inclusion_bounds`][] and
    [`frequenz.api.common.metrics_pb2.Metric.system_exclusion_bounds`][] for more
    details.
    """

    frequency: float
    """AC frequency, in Hertz (Hz)."""

    component_state: InverterComponentState
    """State of the inverter."""

    errors: list[InverterError]
    """List of errors from the component."""

    @classmethod
    def from_proto(cls, raw: microgrid.ComponentData) -> Self:
        """Create InverterData from a protobuf message.

        Args:
            raw: raw component data as decoded from the wire.

        Returns:
            Instance of InverterData created from the protobuf message.
        """
        raw_power = raw.inverter.data.ac.power_active
        inverter_data = cls(
            component_id=raw.id,
            timestamp=raw.ts,
            active_power=raw.inverter.data.ac.power_active.value,
            active_power_per_phase=(
                raw.inverter.data.ac.phase_1.power_active.value,
                raw.inverter.data.ac.phase_2.power_active.value,
                raw.inverter.data.ac.phase_3.power_active.value,
            ),
            reactive_power=raw.inverter.data.ac.power_reactive.value,
            reactive_power_per_phase=(
                raw.inverter.data.ac.phase_1.power_reactive.value,
                raw.inverter.data.ac.phase_2.power_reactive.value,
                raw.inverter.data.ac.phase_3.power_reactive.value,
            ),
            current_per_phase=(
                raw.inverter.data.ac.phase_1.current.value,
                raw.inverter.data.ac.phase_2.current.value,
                raw.inverter.data.ac.phase_3.current.value,
            ),
            voltage_per_phase=(
                raw.inverter.data.ac.phase_1.voltage.value,
                raw.inverter.data.ac.phase_2.voltage.value,
                raw.inverter.data.ac.phase_3.voltage.value,
            ),
            active_power_inclusion_lower_bound=raw_power.system_inclusion_bounds.lower,
            active_power_exclusion_lower_bound=raw_power.system_exclusion_bounds.lower,
            active_power_inclusion_upper_bound=raw_power.system_inclusion_bounds.upper,
            active_power_exclusion_upper_bound=raw_power.system_exclusion_bounds.upper,
            frequency=raw.inverter.data.ac.frequency.value,
            component_state=InverterComponentState.from_pb(
                raw.inverter.state.component_state
            ),
            errors=[InverterError.from_pb(e) for e in raw.inverter.errors],
        )

        inverter_data._set_raw(raw=raw)
        return inverter_data


@dataclass(frozen=True)
class EVChargerData(ComponentData):  # pylint: disable=too-many-instance-attributes
    """A wrapper class for holding ev_charger data."""

    active_power: float
    """The total active 3-phase AC power, in Watts (W).

    Represented in the passive sign convention.

    * Positive means consumption from the grid.
    * Negative means supply into the grid.
    """

    active_power_per_phase: tuple[float, float, float]
    """The per-phase AC active power for phase 1, 2, and 3 respectively, in Watt (W).

    Represented in the passive sign convention.

    * Positive means consumption from the grid.
    * Negative means supply into the grid.
    """

    current_per_phase: tuple[float, float, float]
    """AC current in Amperes (A) for phase/line 1,2 and 3 respectively.

    Represented in the passive sign convention.

    * Positive means consumption from the grid.
    * Negative means supply into the grid.
    """

    reactive_power: float
    """The total reactive 3-phase AC power, in Volt-Ampere Reactive (VAr).

    * Positive power means capacitive (current leading w.r.t. voltage).
    * Negative power means inductive (current lagging w.r.t. voltage).
    """

    reactive_power_per_phase: tuple[float, float, float]
    """The per-phase AC reactive power, in Volt-Ampere Reactive (VAr).

    The provided values are for phase 1, 2, and 3 respectively.

    * Positive power means capacitive (current leading w.r.t. voltage).
    * Negative power means inductive (current lagging w.r.t. voltage).
    """

    voltage_per_phase: tuple[float, float, float]
    """The AC voltage in Volts (V) between the line and the neutral
        wire for phase/line 1,2 and 3 respectively.
    """

    active_power_inclusion_lower_bound: float
    """Lower inclusion bound for EV charger power in watts.

    This is the lower limit of the range within which power requests are allowed for the
    EV charger.

    See [`frequenz.api.common.metrics_pb2.Metric.system_inclusion_bounds`][] and
    [`frequenz.api.common.metrics_pb2.Metric.system_exclusion_bounds`][] for more
    details.
    """

    active_power_exclusion_lower_bound: float
    """Lower exclusion bound for EV charger power in watts.

    This is the lower limit of the range within which power requests are not allowed for
    the EV charger.

    See [`frequenz.api.common.metrics_pb2.Metric.system_inclusion_bounds`][] and
    [`frequenz.api.common.metrics_pb2.Metric.system_exclusion_bounds`][] for more
    details.
    """

    active_power_inclusion_upper_bound: float
    """Upper inclusion bound for EV charger power in watts.

    This is the upper limit of the range within which power requests are allowed for the
    EV charger.

    See [`frequenz.api.common.metrics_pb2.Metric.system_inclusion_bounds`][] and
    [`frequenz.api.common.metrics_pb2.Metric.system_exclusion_bounds`][] for more
    details.
    """

    active_power_exclusion_upper_bound: float
    """Upper exclusion bound for EV charger power in watts.

    This is the upper limit of the range within which power requests are not allowed for
    the EV charger.

    See [`frequenz.api.common.metrics_pb2.Metric.system_inclusion_bounds`][] and
    [`frequenz.api.common.metrics_pb2.Metric.system_exclusion_bounds`][] for more
    details.
    """

    frequency: float
    """AC frequency, in Hertz (Hz)."""

    cable_state: EVChargerCableState
    """The state of the ev charger's cable."""

    component_state: EVChargerComponentState
    """The state of the ev charger."""

    @classmethod
    def from_proto(cls, raw: microgrid.ComponentData) -> Self:
        """Create EVChargerData from a protobuf message.

        Args:
            raw: raw component data as decoded from the wire.

        Returns:
            Instance of EVChargerData created from the protobuf message.
        """
        raw_power = raw.ev_charger.data.ac.power_active
        ev_charger_data = cls(
            component_id=raw.id,
            timestamp=raw.ts,
            active_power=raw_power.value,
            active_power_per_phase=(
                raw.ev_charger.data.ac.phase_1.power_active.value,
                raw.ev_charger.data.ac.phase_2.power_active.value,
                raw.ev_charger.data.ac.phase_3.power_active.value,
            ),
            reactive_power=raw.ev_charger.data.ac.power_reactive.value,
            reactive_power_per_phase=(
                raw.ev_charger.data.ac.phase_1.power_reactive.value,
                raw.ev_charger.data.ac.phase_2.power_reactive.value,
                raw.ev_charger.data.ac.phase_3.power_reactive.value,
            ),
            current_per_phase=(
                raw.ev_charger.data.ac.phase_1.current.value,
                raw.ev_charger.data.ac.phase_2.current.value,
                raw.ev_charger.data.ac.phase_3.current.value,
            ),
            voltage_per_phase=(
                raw.ev_charger.data.ac.phase_1.voltage.value,
                raw.ev_charger.data.ac.phase_2.voltage.value,
                raw.ev_charger.data.ac.phase_3.voltage.value,
            ),
            active_power_inclusion_lower_bound=raw_power.system_inclusion_bounds.lower,
            active_power_exclusion_lower_bound=raw_power.system_exclusion_bounds.lower,
            active_power_inclusion_upper_bound=raw_power.system_inclusion_bounds.upper,
            active_power_exclusion_upper_bound=raw_power.system_exclusion_bounds.upper,
            cable_state=EVChargerCableState.from_pb(raw.ev_charger.state.cable_state),
            component_state=EVChargerComponentState.from_pb(
                raw.ev_charger.state.component_state
            ),
            frequency=raw.ev_charger.data.ac.frequency.value,
        )
        ev_charger_data._set_raw(raw=raw)
        return ev_charger_data

    def is_ev_connected(self) -> bool:
        """Check whether an EV is connected to the charger.

        Returns:
            When the charger is not in an error state, whether an EV is connected to
                the charger.
        """
        return self.component_state not in (
            EVChargerComponentState.AUTHORIZATION_REJECTED,
            EVChargerComponentState.ERROR,
        ) and self.cable_state in (
            EVChargerCableState.EV_LOCKED,
            EVChargerCableState.EV_PLUGGED,
        )
