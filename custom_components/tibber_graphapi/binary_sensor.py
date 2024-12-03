import logging

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import STATE_OFF
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from custom_components.tibber_graphapi import TibberGraphApiDataUpdateCoordinator, TibberGraphApiEntity
from custom_components.tibber_graphapi.const import (
    DOMAIN,
    BINARY_SENSORS,
    ExtBinarySensorEntityDescription
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry, add_entity_cb: AddEntitiesCallback):
    _LOGGER.debug("BINARY_SENSOR async_setup_entry")
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    entities = []
    for description in BINARY_SENSORS:
        entity = TibberGraphApiBinarySensor(coordinator, description)
        entities.append(entity)

    add_entity_cb(entities)


class TibberGraphApiBinarySensor(TibberGraphApiEntity, BinarySensorEntity):
    def __init__(self, coordinator: TibberGraphApiDataUpdateCoordinator, description: ExtBinarySensorEntityDescription):
        super().__init__(coordinator=coordinator, description=description)
        self._attr_icon_off = self.entity_description.icon_off

    @property
    def is_on(self) -> bool | None:
        try:
            if self.coordinator.data is not None:
                if hasattr(self.entity_description, "tag"):
                    # jpath is set ?! ["key1", "child2"]]
                    if self.entity_description.tag.jpath is not None and len(self.entity_description.tag.jpath) > 0:
                        path = self.entity_description.tag.jpath
                        value = self.get_value_in_path(self.coordinator.data, path)

                    elif self.entity_description.tag.jkey is not None:
                        value = self.coordinator.data[self.entity_description.tag.jkey]

                        # have we a key/value map ?!
                        if isinstance(value, list) and "key" in value[0]:
                            if self.entity_description.tag.jvaluekey is not None:
                                for item in value:
                                    if item["key"] == self.entity_description.tag.jvaluekey:
                                        value = item["value"]

        except (IndexError, ValueError, TypeError):
            pass

        if not isinstance(value, bool):
            if isinstance(value, str):
                # parse anything else then 'on' to False!
                if value.lower() == 'on':
                    value = True
                else:
                    value = False
            else:
                value = False

        return value

    @property
    def icon(self):
        """Return the icon of the sensor."""
        if self._attr_icon_off is not None and self.state == STATE_OFF:
            return self._attr_icon_off
        else:
            return super().icon
