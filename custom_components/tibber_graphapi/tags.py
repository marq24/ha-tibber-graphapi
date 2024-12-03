import logging
from enum import Enum
from typing import (
    NamedTuple, Final
)

_LOGGER: logging.Logger = logging.getLogger(__package__)

class ApiKey(NamedTuple):
    key: str
    jpath: list[str] = None
    jkey: str = None
    jvaluekey: str = None
    writeable: bool = False
    writeonly: bool = False

class TGATag(ApiKey, Enum):

    def __hash__(self) -> int:
        return hash(self.key)

    def __str__(self):
        return self.key

    VEH_SOC             = ApiKey(key="soc",                 jpath=["battery", "level"])
    VEH_RANGE           = ApiKey(key="range",               jpath=["battery", "estimatedRange"])
    VEH_SOCMIN          = ApiKey(key="soc_min",             jkey="userSettings", jvaluekey="online.vehicle.smartCharging.minChargeLimit")
    VEH_SOCMAX          = ApiKey(key="soc_max",             jkey="userSettings", jvaluekey="online.vehicle.smartCharging.targetBatteryLevel")
    VEH_CHARGING_STATUS = ApiKey(key="evcc_charging_code",  jkey="chargingStatus")
    VEH_PIN_REQUIRED    = ApiKey(key="enter_pincode",       jkey="enterPincode")
    VEH_ALIVE           = ApiKey(key="alive",               jkey="isAlive")