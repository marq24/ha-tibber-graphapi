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

SENSOR_TYPES = [

    SensorEntityDescription(
        key="soc",
        name="Battery Level",
        icon="mdi:car-electric-outline",
        device_class=None,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=PERCENTAGE,
        suggested_display_precision=0
    ),
    SensorEntityDescription(
        key="range",
        name="Range",
        icon="mdi:ev-station",
        device_class=None,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfLength.KILOMETERS,
        suggested_display_precision=0
    ),
]
