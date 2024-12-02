import logging

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.helpers.typing import StateType

from . import TibberGraphApiDataUpdateCoordinator, TibberGraphApiEntity
from .const import (
    DOMAIN,
    SENSOR_TYPES
)

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities):
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    entities = []

    for description in SENSOR_TYPES:
        entity = TibberGraphApiSensor(coordinator, description)
        entities.append(entity)

    async_add_entities(entities)


class TibberGraphApiSensor(TibberGraphApiEntity, SensorEntity, RestoreEntity):
    def __init__(self, a_coordinator: TibberGraphApiDataUpdateCoordinator, a_description: SensorEntityDescription):
        super().__init__(coordinator=a_coordinator, description=a_description)

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

    # from https://github.com/evcc-io/evcc/blob/master/api/chargemodestatus.go
    # StatusA    ChargeStatus = "A" // Fzg. angeschlossen: nein    Laden aktiv: nein    Ladestation betriebsbereit, Fahrzeug getrennt
    # StatusB    ChargeStatus = "B" // Fzg. angeschlossen:   ja    Laden aktiv: nein    Fahrzeug verbunden, Netzspannung liegt nicht an
    # StatusC    ChargeStatus = "C" // Fzg. angeschlossen:   ja    Laden aktiv:   ja    Fahrzeug lädt, Netzspannung liegt an
    # StatusD    ChargeStatus = "D" // Fzg. angeschlossen:   ja    Laden aktiv:   ja    Fahrzeug lädt mit externer Belüfungsanforderung (für Blei-Säure-Batterien)
    # StatusE    ChargeStatus = "E" // Fzg. angeschlossen:   ja    Laden aktiv: nein    Fehler Fahrzeug / Kabel (CP-Kurzschluss, 0V)
    # StatusF    ChargeStatus = "F" // Fzg. angeschlossen:   ja    Laden aktiv: nein    Fehler EVSE oder Abstecken simulieren (CP-Wake-up, -12V)

    @property
    def native_value(self) -> StateType:
        try:
            if self.coordinator.data is not None:
                if hasattr(self.entity_description, "tag") and self.entity_description.tag.jpath is not None and len(self.entity_description.tag.jpath) > 0:
                    path = self.entity_description.tag.jpath
                    return self.get_value_in_path(self.coordinator.data, path)

        except (IndexError, ValueError, TypeError):
            pass

        return None
