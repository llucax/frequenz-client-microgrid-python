# License: MIT
# Copyright © 2022 Frequenz Energy-as-a-Service GmbH

"""Tests for the microgrid component data."""

from datetime import datetime, timezone

import pytest

# pylint: disable=no-name-in-module
from frequenz.api.common.metrics.electrical_pb2 import AC as PbAc
from frequenz.api.common.metrics_pb2 import Bounds as PbBounds
from frequenz.api.common.metrics_pb2 import Metric as PbMetric
from frequenz.api.microgrid.inverter_pb2 import (
    ComponentState as PbInverterComponentState,
)
from frequenz.api.microgrid.inverter_pb2 import Data as PbInverterData
from frequenz.api.microgrid.inverter_pb2 import Error as PbInverterError
from frequenz.api.microgrid.inverter_pb2 import Inverter as PbInverter
from frequenz.api.microgrid.inverter_pb2 import State as PbInverterState
from frequenz.api.microgrid.microgrid_pb2 import ComponentData as PbComponentData
from google.protobuf.timestamp_pb2 import Timestamp

# pylint: enable=no-name-in-module
from frequenz.client.microgrid import (
    ComponentData,
    InverterComponentState,
    InverterData,
    InverterError,
)


def test_component_data_abstract_class() -> None:
    """Verify the base class ComponentData may not be instantiated."""
    with pytest.raises(TypeError):
        # pylint: disable=abstract-class-instantiated
        ComponentData(0, datetime.now(timezone.utc))  # type: ignore


def test_inverter_data() -> None:
    """Verify the constructor for the InverterData class."""
    seconds = 1234567890

    raw = PbComponentData(
        id=5,
        ts=Timestamp(seconds=seconds),
        inverter=PbInverter(
            state=PbInverterState(
                component_state=PbInverterComponentState.COMPONENT_STATE_DISCHARGING
            ),
            errors=[PbInverterError(msg="error message")],
            data=PbInverterData(
                ac=PbAc(
                    frequency=PbMetric(value=50.1),
                    power_active=PbMetric(
                        value=100.2,
                        system_exclusion_bounds=PbBounds(lower=-501.0, upper=501.0),
                        system_inclusion_bounds=PbBounds(
                            lower=-51_000.0, upper=51_000.0
                        ),
                    ),
                    power_reactive=PbMetric(
                        value=200.3,
                        system_exclusion_bounds=PbBounds(lower=-502.0, upper=502.0),
                        system_inclusion_bounds=PbBounds(
                            lower=-52_000.0, upper=52_000.0
                        ),
                    ),
                    phase_1=PbAc.ACPhase(
                        current=PbMetric(value=12.3),
                        voltage=PbMetric(value=229.8),
                        power_active=PbMetric(value=33.1),
                        power_reactive=PbMetric(value=10.1),
                    ),
                    phase_2=PbAc.ACPhase(
                        current=PbMetric(value=23.4),
                        voltage=PbMetric(value=230.0),
                        power_active=PbMetric(value=33.3),
                        power_reactive=PbMetric(value=10.2),
                    ),
                    phase_3=PbAc.ACPhase(
                        current=PbMetric(value=34.5),
                        voltage=PbMetric(value=230.2),
                        power_active=PbMetric(value=33.8),
                        power_reactive=PbMetric(value=10.3),
                    ),
                ),
            ),
        ),
    )

    inv_data = InverterData.from_proto(raw)
    assert inv_data.component_id == 5
    assert inv_data.timestamp == datetime.fromtimestamp(seconds, timezone.utc)
    assert inv_data.component_state is InverterComponentState.DISCHARGING
    assert inv_data.errors == [InverterError(message="error message")]
    assert inv_data.frequency == pytest.approx(50.1)
    assert inv_data.active_power == pytest.approx(100.2)
    assert inv_data.active_power_per_phase == pytest.approx((33.1, 33.3, 33.8))
    assert inv_data.reactive_power == pytest.approx(200.3)
    assert inv_data.reactive_power_per_phase == pytest.approx((10.1, 10.2, 10.3))
    assert inv_data.current_per_phase == pytest.approx((12.3, 23.4, 34.5))
    assert inv_data.voltage_per_phase == pytest.approx((229.8, 230.0, 230.2))
    assert inv_data.active_power_inclusion_lower_bound == pytest.approx(-51_000.0)
    assert inv_data.active_power_inclusion_upper_bound == pytest.approx(51_000.0)
    assert inv_data.active_power_exclusion_lower_bound == pytest.approx(-501.0)
    assert inv_data.active_power_exclusion_upper_bound == pytest.approx(501.0)
