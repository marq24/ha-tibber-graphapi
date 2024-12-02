from custom_components.tibber_graphapi.tags import TGATag
from typing import Final

from homeassistant.components.sensor import (
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import (
    PERCENTAGE,
    UnitOfLength
)

DOMAIN: Final = "tibber_graphapi"
MANUFACTURE: Final = "Tibber"

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

class ExtSensorEntityDescription(SensorEntityDescription, frozen_or_thawed=True):
    tag: TGATag | None = None

SENSOR_TYPES = [
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
        tag=TGATag.VEH_RANGE,
        key=TGATag.VEH_RANGE.key,
        name="Range",
        icon="mdi:ev-station",
        device_class=None,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfLength.KILOMETERS,
        suggested_display_precision=0
    ),
]
