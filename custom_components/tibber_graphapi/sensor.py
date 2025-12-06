import logging

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.helpers.typing import StateType

from custom_components.tibber_graphapi import TibberGraphApiDataUpdateCoordinator, TibberGraphApiEntity
from custom_components.tibber_graphapi.const import (
    DOMAIN,
    SENSOR_TYPES
)
from custom_components.tibber_graphapi.tags import TGATag

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities):
    _LOGGER.debug("SENSOR async_setup_entry")
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    entities = []

    for description in SENSOR_TYPES:
        entity = TibberGraphApiSensor(coordinator, description)
        entities.append(entity)

    async_add_entities(entities)


class TibberGraphApiSensor(TibberGraphApiEntity, SensorEntity, RestoreEntity):
    def __init__(self, a_coordinator: TibberGraphApiDataUpdateCoordinator, description: SensorEntityDescription):
        super().__init__(coordinator=a_coordinator, description=description)

    def get_value_in_path(self, data, keys):
        return self.get_value_in_path(data[keys[0]], keys[1:]) if keys else data

    # from EVCC [https://github.com/evcc-io/evcc/blob/master/vehicle/ford/provider.go]...
    # func (v *Provider) Status() (api.ChargeStatus, error) {
    #     status := api.StatusNone
    #
    # res, err := v.statusG()
    # if err == nil {
    #     switch res.Metrics.XevPlugChargerStatus.Value {
    #     case "DISCONNECTED":
    #       status = api.StatusA // disconnected
    #     case "CONNECTED":
    #       status = api.StatusB // connected, not charging
    #     case "CHARGING", "CHARGINGAC":
    #       status = api.StatusC // charging
    #     default:
    #       err = fmt.Errorf("unknown charge status: %s", res.Metrics.XevPlugChargerStatus.Value)
    #     }
    # }

    def is_not_null(self, value) -> bool:
        return value is not None and value != "" and value != "null"

    @property
    def native_value(self) -> StateType:
        try:
            if self.coordinator.data is not None:
                if hasattr(self.entity_description, "tag"):
                    # hardcoded charging status A-F
                    if self.entity_description.tag.key == TGATag.VEH_CHARGING_STATUS.key:

                        if TGATag.VEH_CHARGING_STATUS.jkey in self.coordinator.data:
                            # from https://github.com/evcc-io/evcc/blob/master/api/chargemodestatus.go
                            # StatusA    ChargeStatus = "A" // Fzg. angeschlossen: nein    Laden aktiv: nein    Ladestation betriebsbereit, Fahrzeug getrennt
                            # StatusB    ChargeStatus = "B" // Fzg. angeschlossen:   ja    Laden aktiv: nein    Fahrzeug verbunden, Netzspannung liegt nicht an
                            # StatusC    ChargeStatus = "C" // Fzg. angeschlossen:   ja    Laden aktiv:   ja    Fahrzeug lädt, Netzspannung liegt an
                            # StatusD    ChargeStatus = "D" // Fzg. angeschlossen:   ja    Laden aktiv:   ja    Fahrzeug lädt mit externer Belüfungsanforderung (für Blei-Säure-Batterien)
                            # StatusE    ChargeStatus = "E" // Fzg. angeschlossen:   ja    Laden aktiv: nein    Fehler Fahrzeug / Kabel (CP-Kurzschluss, 0V)
                            # StatusF    ChargeStatus = "F" // Fzg. angeschlossen:   ja    Laden aktiv: nein    Fehler EVSE oder Abstecken simulieren (CP-Wake-up, -12V)

                            charging_status = self.coordinator.data[TGATag.VEH_CHARGING_STATUS.jkey].lower()
                            is_charging_status = charging_status == "charging" or charging_status == "chargingac"

                            # tibber graph api is very optimistic with charging status
                            if is_charging_status:
                                isChargingFlag = self.coordinator.data["isCharging"]
                                charging_obj = self.coordinator.data["charging"]
                                has_charger_id = self.is_not_null(charging_obj["chargerId"])
                                progress_obj = charging_obj["progress"]
                                has_progress = self.is_not_null(progress_obj["cost"]) or self.is_not_null(progress_obj["energy"]) or self.is_not_null(progress_obj["speed"])

                                if is_charging_status and (isChargingFlag or has_charger_id or has_progress):
                                    return "C"
                                else:
                                    # A or B ????
                                    return "B"
                            else:
                                if charging_status == "not_charging":
                                    return "B"
                                elif charging_status == "disconnected":
                                    return "A"

                            # if we can not read any value, we return "A" as default
                            return "A"

                    else:
                        # jpath is set ?! ["key1", "child2"]]
                        if self.entity_description.tag.jpath is not None and len(self.entity_description.tag.jpath) > 0:
                            path = self.entity_description.tag.jpath
                            return self.get_value_in_path(self.coordinator.data, path)

                        elif self.entity_description.tag.jkey is not None:
                            value = self.coordinator.data[self.entity_description.tag.jkey]

                            # have we a key/value map ?!
                            if isinstance(value, list) and "key" in value[0]:
                                if self.entity_description.tag.jvaluekey is not None:
                                    for item in value:
                                        if item["key"] == self.entity_description.tag.jvaluekey:
                                            return item["value"]

        except (IndexError, ValueError, TypeError) as ex:
            _LOGGER.warning(f"Error for sensor '{self.entity_description.key}': {ex}")

        return None
