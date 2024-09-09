# License: MIT
# Copyright © 2024 Frequenz Energy-as-a-Service GmbH

"""Loading of Component objects from protobuf messages."""

import logging
from typing import Sequence, assert_never

from frequenz.api.common.v1.microgrid.components import (
    battery_pb2,
    components_pb2,
    ev_charger_pb2,
    fuse_pb2,
    grid_pb2,
    inverter_pb2,
    transformer_pb2,
)
from google.protobuf.json_format import MessageToDict

from .._id import ComponentId, MicrogridId
from .._lifetime import Lifetime
from .._lifetime_proto import lifetime_from_proto
from .._util import enum_from_proto
from ..metrics._bounds import Bounds
from ..metrics._bounds_proto import bounds_from_proto
from ..metrics._metric import Metric
from ._battery import (
    BatteryType,
    BatteryTypes,
    LiIonBattery,
    NaIonBattery,
    UnrecognizedBattery,
    UnspecifiedBattery,
)
from ._category import ComponentCategory
from ._chp import Chp
from ._component import ComponentTypes
from ._converter import Converter
from ._crypto_miner import CryptoMiner
from ._electrolyzer import Electrolyzer
from ._ev_charger import (
    AcEvCharger,
    DcEvCharger,
    EvChargerType,
    EvChargerTypes,
    HybridEvCharger,
    UnrecognizedEvCharger,
    UnspecifiedEvCharger,
)
from ._fuse import Fuse
from ._grid_connection_point import GridConnectionPoint
from ._hvac import Hvac
from ._inverter import (
    BatteryInverter,
    HybridInverter,
    InverterType,
    InverterTypes,
    SolarInverter,
    UnrecognizedInverter,
    UnspecifiedInverter,
)
from ._meter import Meter
from ._precharger import Precharger
from ._problematic import (
    MismatchedCategoryComponent,
    UnrecognizedComponent,
    UnspecifiedComponent,
)
from ._relay import Relay
from ._status import ComponentStatus
from ._voltage_transformer import VoltageTransformer

_logger = logging.getLogger(__name__)


# We disable the `too-many-arguments` check in the whole file because all _from_proto
# functions are expected to take many arguments.
# pylint: disable=too-many-arguments


def component_from_proto(message: components_pb2.Component) -> ComponentTypes:
    """Convert a protobuf message to a `Component` instance.

    Args:
        message: The protobuf message.

    Returns:
        The resulting `Component` instance.
    """
    major_issues: list[str] = []
    minor_issues: list[str] = []

    component = _component_from_proto_with_issues(
        message, major_issues=major_issues, minor_issues=minor_issues
    )

    if major_issues:
        _logger.warning(
            "Found issues in component: %s | Protobuf message:\n%s",
            ", ".join(major_issues),
            message,
        )
    if minor_issues:
        _logger.debug(
            "Found minor issues in component: %s | Protobuf message:\n%s",
            ", ".join(minor_issues),
            message,
        )

    return component


def _component_from_proto_with_issues(
    message: components_pb2.Component,
    *,
    major_issues: list[str],
    minor_issues: list[str],
) -> ComponentTypes:
    """Convert a protobuf message to a `Component` instance and collect issues.

    Args:
        message: The protobuf message.
        major_issues: A list to append major issues to.
        minor_issues: A list to append minor issues to.

    Returns:
        The resulting `Component` instance.
    """
    component_id = ComponentId(message.id)
    microgrid_id = MicrogridId(message.microgrid_id)

    name = message.name or None
    if name is None:
        minor_issues.append("name is empty")

    manufacturer = message.manufacturer or None
    if manufacturer is None:
        minor_issues.append("manufacturer is empty")

    model_name = message.model_name or None
    if model_name is None:
        minor_issues.append("model_name is empty")

    status = enum_from_proto(message.status, ComponentStatus)
    if status is ComponentStatus.UNSPECIFIED:
        major_issues.append("status is unspecified")
    elif isinstance(status, int):
        major_issues.append("status is unrecognized")

    category = enum_from_proto(message.category, ComponentCategory)
    if category is ComponentCategory.UNSPECIFIED:
        major_issues.append("category is unspecified")
    elif isinstance(category, int):
        major_issues.append("category is unrecognized")

    lifetime = _get_operational_lifetime_from_proto(
        message, major_issues=major_issues, minor_issues=minor_issues
    )

    rated_bounds = _metric_config_bounds_from_proto(
        message.metric_config_bounds,
        major_issues=major_issues,
        minor_issues=minor_issues,
    )

    metadata_category = message.category_type.WhichOneof("metadata")
    if (
        metadata_category
        and isinstance(category, ComponentCategory)
        and _category_matches(metadata_category, category)
    ):
        major_issues.append("category_type.metadata does not match the category_type")
        return MismatchedCategoryComponent(
            id=component_id,
            microgrid_id=microgrid_id,
            name=message.name,
            manufacturer=message.manufacturer,
            model_name=message.model_name,
            status=status,
            category=category,
            operational_lifetime=lifetime,
            category_specific_metadata=MessageToDict(
                getattr(message.category_type, metadata_category),
                always_print_fields_with_no_presence=True,
            ),
            rated_bounds=rated_bounds,
        )

    match category:
        case ComponentCategory.UNSPECIFIED:
            major_issues.append("category_type is unspecified")
            return UnspecifiedComponent(
                id=component_id,
                microgrid_id=microgrid_id,
                name=message.name,
                manufacturer=message.manufacturer,
                model_name=message.model_name,
                status=status,
                operational_lifetime=lifetime,
                rated_bounds=rated_bounds,
            )
        case int():
            major_issues.append("category_type is unrecognized")
            return UnrecognizedComponent(
                id=component_id,
                microgrid_id=microgrid_id,
                name=message.name,
                manufacturer=message.manufacturer,
                model_name=message.model_name,
                status=status,
                category=category,
                operational_lifetime=lifetime,
                rated_bounds=rated_bounds,
            )
        case ComponentCategory.BATTERY:
            return _battery_from_proto(
                message=message.category_type.battery,
                component_id=component_id,
                microgrid_id=microgrid_id,
                name=message.name,
                manufacturer=message.manufacturer,
                model_name=message.model_name,
                status=status,
                operational_lifetime=lifetime,
                rated_bounds=rated_bounds,
            )
        case ComponentCategory.CHP:
            return Chp(
                id=component_id,
                microgrid_id=microgrid_id,
                name=message.name,
                manufacturer=message.manufacturer,
                model_name=message.model_name,
                status=status,
                operational_lifetime=lifetime,
                rated_bounds=rated_bounds,
            )
        case ComponentCategory.CONVERTER:
            return Converter(
                id=component_id,
                microgrid_id=microgrid_id,
                name=message.name,
                manufacturer=message.manufacturer,
                model_name=message.model_name,
                status=status,
                operational_lifetime=lifetime,
                rated_bounds=rated_bounds,
            )
        case ComponentCategory.CRYPTO_MINER:
            return CryptoMiner(
                id=component_id,
                microgrid_id=microgrid_id,
                name=message.name,
                manufacturer=message.manufacturer,
                model_name=message.model_name,
                status=status,
                operational_lifetime=lifetime,
                rated_bounds=rated_bounds,
            )
        case ComponentCategory.ELECTROLYZER:
            return Electrolyzer(
                id=component_id,
                microgrid_id=microgrid_id,
                name=message.name,
                manufacturer=message.manufacturer,
                model_name=message.model_name,
                status=status,
                operational_lifetime=lifetime,
                rated_bounds=rated_bounds,
            )
        case ComponentCategory.EV_CHARGER:
            return _ev_charger_from_proto(
                message=message.category_type.ev_charger,
                component_id=component_id,
                microgrid_id=microgrid_id,
                name=message.name,
                manufacturer=message.manufacturer,
                model_name=message.model_name,
                status=status,
                operational_lifetime=lifetime,
                rated_bounds=rated_bounds,
            )
        case ComponentCategory.FUSE:
            return _fuse_from_proto(
                message=message.category_type.fuse,
                component_id=component_id,
                microgrid_id=microgrid_id,
                name=message.name,
                manufacturer=message.manufacturer,
                model_name=message.model_name,
                status=status,
                operational_lifetime=lifetime,
                rated_bounds=rated_bounds,
            )
        case ComponentCategory.GRID:
            return _grid_connection_point_from_proto(
                message=message.category_type.grid,
                component_id=component_id,
                microgrid_id=microgrid_id,
                name=message.name,
                manufacturer=message.manufacturer,
                model_name=message.model_name,
                status=status,
                operational_lifetime=lifetime,
                rated_bounds=rated_bounds,
            )
        case ComponentCategory.HVAC:
            return Hvac(
                id=component_id,
                microgrid_id=microgrid_id,
                name=message.name,
                manufacturer=message.manufacturer,
                model_name=message.model_name,
                status=status,
                operational_lifetime=lifetime,
                rated_bounds=rated_bounds,
            )
        case ComponentCategory.INVERTER:
            return _inverter_from_proto(
                message=message.category_type.inverter,
                component_id=component_id,
                microgrid_id=microgrid_id,
                name=message.name,
                manufacturer=message.manufacturer,
                model_name=message.model_name,
                status=status,
                operational_lifetime=lifetime,
                rated_bounds=rated_bounds,
            )
        case ComponentCategory.METER:
            return Meter(
                id=component_id,
                microgrid_id=microgrid_id,
                name=message.name,
                manufacturer=message.manufacturer,
                model_name=message.model_name,
                status=status,
                operational_lifetime=lifetime,
                rated_bounds=rated_bounds,
            )
        case ComponentCategory.PRECHARGER:
            return Precharger(
                id=component_id,
                microgrid_id=microgrid_id,
                name=message.name,
                manufacturer=message.manufacturer,
                model_name=message.model_name,
                status=status,
                operational_lifetime=lifetime,
                rated_bounds=rated_bounds,
            )
        case ComponentCategory.RELAY:
            return Relay(
                id=component_id,
                microgrid_id=microgrid_id,
                name=message.name,
                manufacturer=message.manufacturer,
                model_name=message.model_name,
                status=status,
                operational_lifetime=lifetime,
                rated_bounds=rated_bounds,
            )
        case ComponentCategory.VOLTAGE_TRANSFORMER:
            return _voltage_transformer_from_proto(
                message=message.category_type.voltage_transformer,
                component_id=component_id,
                microgrid_id=microgrid_id,
                name=message.name,
                manufacturer=message.manufacturer,
                model_name=message.model_name,
                status=status,
                operational_lifetime=lifetime,
                rated_bounds=rated_bounds,
            )
        case unexpected_category:
            assert_never(unexpected_category)


def _category_matches(metadata_category: str, category: ComponentCategory) -> bool:
    """Check if the metadata category matches the declared category."""
    category_to_metadata_name_fixes = {
        "grid_connection_point": "grid",
    }
    cat_name = category.name.lower()
    fixed_category = category_to_metadata_name_fixes.get(cat_name, cat_name)
    return fixed_category != metadata_category


def _battery_from_proto(
    *,
    message: battery_pb2.Battery,
    component_id: ComponentId,
    microgrid_id: MicrogridId,
    name: str,
    manufacturer: str,
    model_name: str,
    status: ComponentStatus | int,
    operational_lifetime: Lifetime,
    rated_bounds: dict[Metric | int, Bounds],
) -> BatteryTypes:
    """Convert a protobuf message to a `Battery` instance."""
    enum_to_class: dict[
        BatteryType, type[UnspecifiedBattery | LiIonBattery | NaIonBattery]
    ] = {
        BatteryType.UNSPECIFIED: UnspecifiedBattery,
        BatteryType.LI_ION: LiIonBattery,
        BatteryType.NA_ION: NaIonBattery,
    }
    battery_type = enum_from_proto(message.type, BatteryType)
    match battery_type:
        case BatteryType.UNSPECIFIED | BatteryType.LI_ION | BatteryType.NA_ION:
            return enum_to_class[battery_type](
                id=component_id,
                microgrid_id=microgrid_id,
                name=name,
                manufacturer=manufacturer,
                model_name=model_name,
                status=status,
                operational_lifetime=operational_lifetime,
                rated_bounds=rated_bounds,
            )
        case int():
            return UnrecognizedBattery(
                id=component_id,
                microgrid_id=microgrid_id,
                name=name,
                manufacturer=manufacturer,
                model_name=model_name,
                status=status,
                operational_lifetime=operational_lifetime,
                rated_bounds=rated_bounds,
                type=battery_type,
            )
        case unexpected:
            assert_never(unexpected)


def _ev_charger_from_proto(
    *,
    message: ev_charger_pb2.EvCharger,
    component_id: ComponentId,
    microgrid_id: MicrogridId,
    name: str,
    manufacturer: str,
    model_name: str,
    status: ComponentStatus | int,
    operational_lifetime: Lifetime,
    rated_bounds: dict[Metric | int, Bounds],
) -> EvChargerTypes:
    """Convert a protobuf message to an `EvCharger` instance."""
    enum_to_class: dict[
        EvChargerType,
        type[UnspecifiedEvCharger | AcEvCharger | DcEvCharger | HybridEvCharger],
    ] = {
        EvChargerType.UNSPECIFIED: UnspecifiedEvCharger,
        EvChargerType.AC: AcEvCharger,
        EvChargerType.DC: DcEvCharger,
        EvChargerType.HYBRID: HybridEvCharger,
    }
    ev_charger_type = enum_from_proto(message.type, EvChargerType)
    match ev_charger_type:
        case (
            EvChargerType.UNSPECIFIED
            | EvChargerType.AC
            | EvChargerType.DC
            | EvChargerType.HYBRID
        ):
            return enum_to_class[ev_charger_type](
                id=component_id,
                microgrid_id=microgrid_id,
                name=name,
                manufacturer=manufacturer,
                model_name=model_name,
                status=status,
                operational_lifetime=operational_lifetime,
                rated_bounds=rated_bounds,
            )
        case int():
            return UnrecognizedEvCharger(
                id=component_id,
                microgrid_id=microgrid_id,
                name=name,
                manufacturer=manufacturer,
                model_name=model_name,
                status=status,
                operational_lifetime=operational_lifetime,
                rated_bounds=rated_bounds,
                type=ev_charger_type,
            )
        case unexpected:
            assert_never(unexpected)


def _fuse_from_proto(
    *,
    message: fuse_pb2.Fuse,
    component_id: ComponentId,
    microgrid_id: MicrogridId,
    name: str,
    manufacturer: str,
    model_name: str,
    status: ComponentStatus | int,
    operational_lifetime: Lifetime,
    rated_bounds: dict[Metric | int, Bounds],
) -> Fuse:
    """Convert a protobuf message to a `Fuse` instance."""
    return Fuse(
        id=component_id,
        microgrid_id=microgrid_id,
        name=name,
        manufacturer=manufacturer,
        model_name=model_name,
        status=status,
        operational_lifetime=operational_lifetime,
        rated_bounds=rated_bounds,
        rated_current=message.rated_current,
    )


def _grid_connection_point_from_proto(
    *,
    message: grid_pb2.GridConnectionPoint,
    component_id: ComponentId,
    microgrid_id: MicrogridId,
    name: str,
    manufacturer: str,
    model_name: str,
    status: ComponentStatus | int,
    operational_lifetime: Lifetime,
    rated_bounds: dict[Metric | int, Bounds],
) -> GridConnectionPoint:
    """Convert a protobuf message to an `GridConnectionPoint` instance."""
    return GridConnectionPoint(
        id=component_id,
        microgrid_id=microgrid_id,
        name=name,
        manufacturer=manufacturer,
        model_name=model_name,
        status=status,
        operational_lifetime=operational_lifetime,
        rated_bounds=rated_bounds,
        rated_fuse_current=message.rated_fuse_current,
    )


def _inverter_from_proto(
    *,
    message: inverter_pb2.Inverter,
    component_id: ComponentId,
    microgrid_id: MicrogridId,
    name: str,
    manufacturer: str,
    model_name: str,
    status: ComponentStatus | int,
    operational_lifetime: Lifetime,
    rated_bounds: dict[Metric | int, Bounds],
) -> InverterTypes:
    """Convert a protobuf message to an `Inverter` instance."""
    enum_to_class: dict[
        InverterType,
        type[UnspecifiedInverter | BatteryInverter | SolarInverter | HybridInverter],
    ] = {
        InverterType.UNSPECIFIED: UnspecifiedInverter,
        InverterType.BATTERY: BatteryInverter,
        InverterType.SOLAR: SolarInverter,
        InverterType.HYBRID: HybridInverter,
    }
    inverter_type = enum_from_proto(message.type, InverterType)
    match inverter_type:
        case (
            InverterType.UNSPECIFIED
            | InverterType.BATTERY
            | InverterType.SOLAR
            | InverterType.HYBRID
        ):
            return enum_to_class[inverter_type](
                id=component_id,
                microgrid_id=microgrid_id,
                name=name,
                manufacturer=manufacturer,
                model_name=model_name,
                status=status,
                operational_lifetime=operational_lifetime,
                rated_bounds=rated_bounds,
            )
        case int():
            return UnrecognizedInverter(
                id=component_id,
                microgrid_id=microgrid_id,
                name=name,
                manufacturer=manufacturer,
                model_name=model_name,
                status=status,
                operational_lifetime=operational_lifetime,
                rated_bounds=rated_bounds,
                type=inverter_type,
            )
        case unexpected:
            assert_never(unexpected)


def _voltage_transformer_from_proto(
    *,
    message: transformer_pb2.VoltageTransformer,
    component_id: ComponentId,
    microgrid_id: MicrogridId,
    name: str,
    manufacturer: str,
    model_name: str,
    status: ComponentStatus | int,
    operational_lifetime: Lifetime,
    rated_bounds: dict[Metric | int, Bounds],
) -> VoltageTransformer:
    """Convert a protobuf message to a `VoltageTransformer` instance."""
    return VoltageTransformer(
        id=component_id,
        microgrid_id=microgrid_id,
        name=name,
        manufacturer=manufacturer,
        model_name=model_name,
        status=status,
        operational_lifetime=operational_lifetime,
        rated_bounds=rated_bounds,
        primary_voltage=message.primary,
        secondary_voltage=message.secondary,
    )


def _metric_config_bounds_from_proto(
    message: Sequence[components_pb2.MetricConfigBounds],
    *,
    major_issues: list[str],
    minor_issues: list[str],  # pylint: disable=unused-argument
) -> dict[Metric | int, Bounds]:
    """Convert a `MetricConfigBounds` message to a dictionary of `Metric` to `Bounds`.

    Args:
        message: The `MetricConfigBounds` message.
        major_issues: A list to append major issues to.
        minor_issues: A list to append minor issues to.

    Returns:
        The resulting dictionary of `Metric` to `Bounds`.
    """
    bounds: dict[Metric | int, Bounds] = {}
    for metric_bound in message:
        metric = enum_from_proto(metric_bound.metric, Metric)
        match metric:
            case Metric.UNSPECIFIED:
                major_issues.append("metric_config_bounds has an UNSPECIFIED metric")
            case int():
                minor_issues.append(
                    f"metric_config_bounds has an unrecognized metric {metric}"
                )

        if not metric_bound.HasField("config_bounds"):
            major_issues.append(
                f"metric_config_bounds for {metric} is present but missing "
                "`config_bounds`, considering it unbounded",
            )
            continue

        try:
            bound = bounds_from_proto(metric_bound.config_bounds)
        except ValueError as exc:
            major_issues.append(
                f"metric_config_bounds for {metric} is invalid ({exc}), considering "
                "it as missing (i.e. unbouded)",
            )
            continue
        if metric in bounds:
            major_issues.append(
                f"metric_config_bounds for {metric} is duplicated in the message"
                f"using the last one ({bound})",
            )
        bounds[metric] = bound

    return bounds


def _get_operational_lifetime_from_proto(
    message: components_pb2.Component,
    *,
    major_issues: list[str],
    minor_issues: list[str],
) -> Lifetime:
    """Get the operational lifetime from a protobuf message."""
    if message.HasField("operational_lifetime"):
        try:
            return lifetime_from_proto(message.operational_lifetime)
        except ValueError as exc:
            major_issues.append(
                f"invalid operational lifetime ({exc}), considering it as missing "
                "(i.e. always operational)",
            )
    else:
        minor_issues.append(
            "missing operational lifetime, considering it always operational",
        )
    return Lifetime()
