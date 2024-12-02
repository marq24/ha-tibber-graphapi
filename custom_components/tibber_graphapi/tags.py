import logging
from enum import Enum
from typing import (
    NamedTuple, Final
)

_LOGGER: logging.Logger = logging.getLogger(__package__)

class CAT(Enum):
    CONFIG = "CONF"
    STATUS = "STAT"
    OTHER = "OTHE"
    CONSTANT = "CONS"

class ApiKey(NamedTuple):
    key: str
    cat: CAT
    jpath: list[str]
    writeable: bool = False
    writeonly: bool = False

class TGATag(ApiKey, Enum):

    def __hash__(self) -> int:
        return hash(self.key)

    def __str__(self):
        return self.key

    VEH_SOC = ApiKey(key="soc", cat=CAT.STATUS, jpath=["battery", "level"])
    VEH_RANGE = ApiKey(key="range", cat=CAT.STATUS, jpath=["battery", "estimatedRange"])
