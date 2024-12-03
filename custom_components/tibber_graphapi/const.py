from custom_components.tibber_graphapi.tags import TGATag
from typing import Final

from homeassistant.components.binary_sensor import BinarySensorEntityDescription
from homeassistant.components.sensor import (
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import (
    PERCENTAGE,
    UnitOfLength,
    EntityCategory
)

DOMAIN: Final = "tibber_graphapi"
MANUFACTURE: Final = "Tibber"

PLATFORMS: Final = ["binary_sensor", "sensor"]

CONF_TIBBER_VEHICLE_ID = "tibber_vehicle_id"
CONF_TIBBER_VEHICLE_NAME = "tibber_vehicle_name"
CONF_VEHINDEX_NUMBER = "vehicle_index_number"

DEFAULT_CONF_NAME = "TGA"
DEFAULT_USERNAME = "your-tibber-account-email"
DEFAULT_PWD = ""
DEFAULT_SCAN_INTERVAL = 60
DEFAULT_VEHINDEX_NUMBER = 0

# for evcc we need the following sensor types!
# https://docs.evcc.io/docs/devices/vehicles#manuell

class ExtBinarySensorEntityDescription(BinarySensorEntityDescription, frozen_or_thawed=True):
    tag: TGATag | None = None
    icon_off: str | None = None

class ExtSensorEntityDescription(SensorEntityDescription, frozen_or_thawed=True):
    tag: TGATag | None = None

BINARY_SENSORS = [
    ExtBinarySensorEntityDescription(
        tag=TGATag.VEH_PIN_REQUIRED,
        key=TGATag.VEH_PIN_REQUIRED.key,
        name="Pin Required",
        icon="mdi:lock-alert",
        icon_off="mdi:lock-open",
        entity_category=EntityCategory.DIAGNOSTIC,
        device_class=None
    ),
    ExtBinarySensorEntityDescription(
        tag=TGATag.VEH_ALIVE,
        key=TGATag.VEH_ALIVE.key,
        name="Alive?",
        icon="mdi:robot",
        icon_off="mdi:robot-dead-outline",
        entity_category=EntityCategory.DIAGNOSTIC,
        device_class=None
    )

]

SENSOR_TYPES = [
    ExtSensorEntityDescription(
        tag=TGATag.VEH_CHARGING_STATUS,
        key=TGATag.VEH_CHARGING_STATUS.key,
        name="EVCC charging status Code",
        icon="mdi:state-machine",
        device_class=None,
        state_class=None,
    ),
    ExtSensorEntityDescription(
        tag=TGATag.VEH_RANGE,
        key=TGATag.VEH_RANGE.key,
        name="Range",
        icon="mdi:ev-station",
        device_class=None,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfLength.KILOMETERS,
        suggested_display_precision=0
    ),
    ExtSensorEntityDescription(
        tag=TGATag.VEH_SOC,
        key=TGATag.VEH_SOC.key,
        name="Battery Level",
        icon="mdi:car-electric-outline",
        device_class=None,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=PERCENTAGE,
        suggested_display_precision=0
    ),
    ExtSensorEntityDescription(
        tag=TGATag.VEH_SOCMAX,
        key=TGATag.VEH_SOCMAX.key,
        name="SOC MAX",
        icon="mdi:battery-charging-100",
        device_class=None,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=PERCENTAGE,
        suggested_display_precision=0
    ),
    ExtSensorEntityDescription(
        tag=TGATag.VEH_SOCMIN,
        key=TGATag.VEH_SOCMIN.key,
        name="SOC min",
        icon="mdi:battery-charging-outline",
        device_class=None,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=PERCENTAGE,
        suggested_display_precision=0
    ),
]
