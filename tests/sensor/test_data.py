# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Tests for the Sensor and sensor data classes."""

from datetime import datetime, timezone
from typing import Any

import pytest
from frequenz.client.common.microgrid.sensors import SensorId

from frequenz.client.microgrid.metrics import (
    AggregatedMetricValue,
    AggregationMethod,
    Metric,
)
from frequenz.client.microgrid.sensor import (
    SensorDataSamples,
    SensorErrorCode,
    SensorMetricSample,
    SensorStateCode,
    SensorStateSample,
)


@pytest.fixture
def now() -> datetime:
    """Fixture to provide the current datetime."""
    return datetime.now(timezone.utc)


@pytest.fixture
def sensor_id() -> SensorId:
    """Provide a test sensor ID."""
    return SensorId(42)


@pytest.fixture
def metric_sample(now: datetime) -> SensorMetricSample:
    """Provide a test sensor metric sample."""
    return SensorMetricSample(
        sampled_at=now,
        metric=Metric.SENSOR_TEMPERATURE,
        value=25.0,
    )


@pytest.fixture
def state_sample(now: datetime) -> SensorStateSample:
    """Provide a test sensor state sample."""
    return SensorStateSample(
        sampled_at=now,
        states=frozenset([SensorStateCode.ON]),
        warnings=frozenset(),
        errors=frozenset(),
    )


class TestSensorMetricSample:
    """Tests for SensorMetricSample class."""

    @pytest.mark.parametrize(
        "metric,value",
        [
            pytest.param(Metric.SENSOR_TEMPERATURE, 5.0, id="single"),
            pytest.param(
                Metric.SENSOR_RELATIVE_HUMIDITY,
                AggregatedMetricValue(
                    avg=5.0,
                    min=1.0,
                    max=10.0,
                    raw_values=[1.0, 5.0, 10.0],
                ),
                id="aggregated",
            ),
            pytest.param(Metric.SENSOR_DEW_POINT, None, id="none"),
        ],
    )
    def test_creation(
        self, now: datetime, metric: Metric, value: float | AggregatedMetricValue | None
    ) -> None:
        """Test creation with different value types."""
        sample = SensorMetricSample(sampled_at=now, metric=metric, value=value)
        assert sample.sampled_at == now
        assert sample.metric == metric
        assert sample.value == value

    @pytest.mark.parametrize(
        "value,method_results",
        [
            pytest.param(
                5.0,
                {
                    AggregationMethod.AVG: 5.0,
                    AggregationMethod.MIN: 5.0,
                    AggregationMethod.MAX: 5.0,
                },
                id="single",
            ),
            pytest.param(
                AggregatedMetricValue(
                    avg=5.0,
                    min=1.0,
                    max=10.0,
                    raw_values=[1.0, 5.0, 10.0],
                ),
                {
                    AggregationMethod.AVG: 5.0,
                    AggregationMethod.MIN: 1.0,
                    AggregationMethod.MAX: 10.0,
                },
                id="aggregated",
            ),
            pytest.param(
                None,
                {
                    AggregationMethod.AVG: None,
                    AggregationMethod.MIN: None,
                    AggregationMethod.MAX: None,
                },
                id="none",
            ),
        ],
    )
    def test_as_single_value(
        self,
        now: datetime,
        value: Any,
        method_results: dict[AggregationMethod, float | None],
    ) -> None:
        """Test as_single_value with different value types and methods."""
        sample = SensorMetricSample(
            sampled_at=now, metric=Metric.SENSOR_TEMPERATURE, value=value
        )

        for method, expected in method_results.items():
            assert sample.as_single_value(aggregation_method=method) == expected


class TestSensorStateSample:
    """Tests for SensorStateSample class."""

    @pytest.mark.parametrize(
        "states,warnings,errors",
        [
            pytest.param(
                frozenset([SensorStateCode.ON]),
                frozenset[SensorErrorCode](),
                frozenset[SensorErrorCode](),
                id="on_state_no_issues",
            ),
            pytest.param(
                frozenset([SensorStateCode.ERROR]),
                frozenset([SensorErrorCode.INTERNAL]),
                frozenset([SensorErrorCode.UNKNOWN]),
                id="error_state_with_issues",
            ),
            pytest.param(
                frozenset([SensorStateCode.ON]),
                frozenset([SensorErrorCode.INTERNAL]),
                frozenset[SensorErrorCode](),
                id="on_state_with_warnings",
            ),
            pytest.param(
                frozenset([999]),  # Unknown state code
                frozenset([888]),  # Unknown warning code
                frozenset([777]),  # Unknown error code
                id="unknown_codes",
            ),
            pytest.param(
                frozenset([SensorStateCode.ON, SensorStateCode.ERROR]),
                frozenset([SensorErrorCode.INTERNAL, SensorErrorCode.UNKNOWN]),
                frozenset([SensorErrorCode.INTERNAL]),
                id="multiple_codes",
            ),
        ],
    )
    def test_creation(
        self,
        now: datetime,
        states: frozenset[SensorStateCode | int],
        warnings: frozenset[SensorErrorCode | int],
        errors: frozenset[SensorErrorCode | int],
    ) -> None:
        """Test with various state combinations."""
        sample = SensorStateSample(
            sampled_at=now,
            states=states,
            warnings=warnings,
            errors=errors,
        )

        assert sample.sampled_at == now
        assert sample.states == states
        assert sample.warnings == warnings
        assert sample.errors == errors

    def test_equality(self, now: datetime) -> None:
        """Test equality of instances."""
        states1 = frozenset([SensorStateCode.ON])
        warnings1 = frozenset([SensorErrorCode.INTERNAL])
        errors1: frozenset[SensorErrorCode] = frozenset()

        sample1 = SensorStateSample(
            sampled_at=now,
            states=states1,
            warnings=warnings1,
            errors=errors1,
        )

        sample2 = SensorStateSample(
            sampled_at=now,
            states=states1,
            warnings=warnings1,
            errors=errors1,
        )

        different_timestamp = SensorStateSample(
            sampled_at=datetime(2025, 3, 1, 13, 0, 0, tzinfo=timezone.utc),
            states=states1,
            warnings=warnings1,
            errors=errors1,
        )

        different_states = SensorStateSample(
            sampled_at=now,
            states=frozenset([SensorStateCode.ERROR]),
            warnings=warnings1,
            errors=errors1,
        )

        different_warnings = SensorStateSample(
            sampled_at=now,
            states=states1,
            warnings=frozenset(),
            errors=errors1,
        )

        different_errors = SensorStateSample(
            sampled_at=now,
            states=states1,
            warnings=warnings1,
            errors=frozenset([SensorErrorCode.UNKNOWN]),
        )

        assert sample1 == sample2
        assert sample1 != different_timestamp
        assert sample1 != different_states
        assert sample1 != different_warnings
        assert sample1 != different_errors


class TestSensorDataSamples:
    """Tests for SensorDataSamples class."""

    @pytest.mark.parametrize(
        "metric_samples,states",
        [
            pytest.param([], [], id="empty"),
            pytest.param(
                [],
                [
                    SensorStateSample(
                        sampled_at=datetime(2025, 1, 1, tzinfo=timezone.utc),
                        states=frozenset([SensorStateCode.ON]),
                        warnings=frozenset(),
                        errors=frozenset(),
                    )
                ],
                id="states_only",
            ),
            pytest.param(
                [
                    SensorMetricSample(
                        sampled_at=datetime(2025, 1, 1, tzinfo=timezone.utc),
                        metric=Metric.SENSOR_TEMPERATURE,
                        value=22.5,
                    )
                ],
                [],
                id="metrics_only",
            ),
            pytest.param(
                [
                    SensorMetricSample(
                        sampled_at=datetime(2025, 1, 1, tzinfo=timezone.utc),
                        metric=Metric.SENSOR_TEMPERATURE,
                        value=22.5,
                    ),
                    SensorMetricSample(
                        sampled_at=datetime(2025, 1, 1, tzinfo=timezone.utc),
                        metric=Metric.SENSOR_RELATIVE_HUMIDITY,
                        value=AggregatedMetricValue(
                            avg=65.0,
                            min=60.0,
                            max=70.0,
                            raw_values=[60.0, 65.0, 70.0],
                        ),
                    ),
                ],
                [
                    SensorStateSample(
                        sampled_at=datetime(2025, 1, 1, tzinfo=timezone.utc),
                        states=frozenset([SensorStateCode.ON]),
                        warnings=frozenset([SensorErrorCode.INTERNAL]),
                        errors=frozenset(),
                    ),
                    SensorStateSample(
                        sampled_at=datetime(2025, 1, 1, tzinfo=timezone.utc),
                        states=frozenset([SensorStateCode.ERROR]),
                        warnings=frozenset(),
                        errors=frozenset([SensorErrorCode.UNKNOWN]),
                    ),
                ],
                id="multiple_samples",
            ),
        ],
    )
    def test_creation(
        self,
        sensor_id: SensorId,
        metric_samples: list[SensorMetricSample],
        states: list[SensorStateSample],
    ) -> None:
        """Test with various sample combinations."""
        data_samples = SensorDataSamples(
            sensor_id=sensor_id,
            metric_samples=metric_samples,
            states=states,
        )

        assert data_samples.sensor_id == sensor_id
        assert data_samples.metric_samples == metric_samples
        assert data_samples.states == states

    def test_equality(
        self,
        sensor_id: SensorId,
        metric_sample: SensorMetricSample,
        state_sample: SensorStateSample,
    ) -> None:
        """Test equality of instances."""
        data_samples1 = SensorDataSamples(
            sensor_id=sensor_id,
            metric_samples=[metric_sample],
            states=[state_sample],
        )

        data_samples2 = SensorDataSamples(
            sensor_id=sensor_id,
            metric_samples=[metric_sample],
            states=[state_sample],
        )

        different_sensor_id = SensorDataSamples(
            sensor_id=SensorId(999),
            metric_samples=[metric_sample],
            states=[state_sample],
        )

        different_metric_samples = SensorDataSamples(
            sensor_id=sensor_id,
            metric_samples=[],
            states=[state_sample],
        )

        different_states = SensorDataSamples(
            sensor_id=sensor_id,
            metric_samples=[metric_sample],
            states=[],
        )

        assert data_samples1 == data_samples2
        assert data_samples1 != different_sensor_id
        assert data_samples1 != different_metric_samples
        assert data_samples1 != different_states
