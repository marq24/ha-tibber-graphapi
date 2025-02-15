import asyncio
import json
import logging
import re
import uuid
from datetime import timedelta
from typing import Final

import voluptuous as vol
from homeassistant.config_entries import ConfigEntry, ConfigEntryState
from homeassistant.const import CONF_USERNAME, CONF_SCAN_INTERVAL, CONF_PASSWORD
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.entity import EntityDescription, Entity
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from custom_components.tibber_graphapi.const import (
    DOMAIN,
    MANUFACTURE,
    PLATFORMS,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_VEHINDEX_NUMBER,
    CONF_VEHINDEX_NUMBER,
    CONF_TIBBER_VEHICLE_ID,
    CONF_TIBBER_VEHICLE_NAME
)

_LOGGER = logging.getLogger(__name__)
SCAN_INTERVAL = timedelta(seconds=10)
CONFIG_SCHEMA = vol.Schema({DOMAIN: vol.Schema({})}, extra=vol.ALLOW_EXTRA)

CC_P1: Final = re.compile(r"(.)([A-Z][a-z]+)")
CC_P2: Final = re.compile(r"([a-z0-9])([A-Z])")

@staticmethod
def _camel_to_snake(a_key: str):
    if a_key.lower().endswith("kwh"):
        a_key = a_key[:-3] + "_kwh"
    a_key = re.sub(CC_P1, r'\1_\2', a_key)
    return re.sub(CC_P2, r'\1_\2', a_key).lower()

def mask_map(d):
    for k, v in d.copy().items():
        if isinstance(v, dict):
            d.pop(k)
            d[k] = v
            mask_map(v)
        else:
            lk = k.lower()
            if lk == "host" or lk == CONF_PASSWORD or lk == CONF_USERNAME:
                v = "<MASKED>"
            d.pop(k)
            d[k] = v
    return d


async def async_setup(hass: HomeAssistant, config: dict):
    return True


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry):
    global SCAN_INTERVAL
    SCAN_INTERVAL = timedelta(seconds=config_entry.options.get(CONF_SCAN_INTERVAL,
                                                               config_entry.data.get(CONF_SCAN_INTERVAL,
                                                                                     DEFAULT_SCAN_INTERVAL)))
    _LOGGER.info(
        f"Starting Tibber GraphAPI with interval: {SCAN_INTERVAL} - ConfigEntry: {mask_map(dict(config_entry.as_dict()))}")

    if DOMAIN not in hass.data:
        value = "UNKOWN"
        hass.data.setdefault(DOMAIN, {"manifest_version": value})

    coordinator = TibberGraphApiDataUpdateCoordinator(hass, config_entry)
    if not coordinator.last_update_success:
        raise ConfigEntryNotReady
    else:
        await coordinator.init_on_load()

    hass.data[DOMAIN][config_entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(config_entry, PLATFORMS)

    if config_entry.state != ConfigEntryState.LOADED:
        config_entry.add_update_listener(async_reload_entry)

    return True


class TibberGraphApiDataUpdateCoordinator(DataUpdateCoordinator):

    def __init__(self, hass: HomeAssistant, config_entry):
        self._user = config_entry.options.get(CONF_USERNAME, config_entry.data[CONF_USERNAME])
        self._vehicle_index = int(config_entry.options.get(CONF_VEHINDEX_NUMBER, config_entry.data.get(CONF_VEHINDEX_NUMBER, DEFAULT_VEHINDEX_NUMBER)))
        self._vehicle_id = config_entry.options.get(CONF_TIBBER_VEHICLE_ID, config_entry.data.get(CONF_TIBBER_VEHICLE_ID, None))
        self._vehicle_name = config_entry.options.get(CONF_TIBBER_VEHICLE_NAME, config_entry.data.get(CONF_TIBBER_VEHICLE_NAME, None))

        the_pwd = config_entry.options.get(CONF_PASSWORD, config_entry.data[CONF_PASSWORD])

        # support for systems where vehicle index is not 0
        self.bridge = TibberGraphApiBridge(user=self._user, pwd=the_pwd,
                                           a_web_session=async_get_clientsession(hass),
                                           veh_index=self._vehicle_index,
                                           veh_id=self._vehicle_id)

        self.name = config_entry.title
        self._config_entry = config_entry
        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=SCAN_INTERVAL)

    async def init_on_load(self):
        try:
            init_data = await self.bridge.update()
            _LOGGER.debug(f"after init - data: '{self.data}'")
            if self.data is None or len(self.data) == 0:
                _LOGGER.debug(f"patch data to: '{init_data}'")
                self.data = init_data

            if self._vehicle_id is None:
                self._vehicle_id = self.bridge.vehicle_id
            _LOGGER.debug(f"init_on_load vehicle_id: '{self._vehicle_id}'")

            if self._vehicle_name is None:
                self._vehicle_name = self.bridge.vehicle_name
            _LOGGER.debug(f"init_on_load vehicle_name: '{self._vehicle_name}'")

        except Exception as exception:
            _LOGGER.warning(f"init caused {exception}")

        # building the static device info...
        self._device_info_dict = {
            "identifiers": {
                ("DOMAIN", DOMAIN),
                ("ID", self._vehicle_id),
            },
            "manufacturer": MANUFACTURE,
            "name": f"Tibber GraphAPI {self._vehicle_name}"
        }

    async def async_refresh_with_pause(self):
        await asyncio.sleep(5)
        await self.async_refresh()

    async def _async_update_data(self):
        _LOGGER.debug(f"_async_update_data called")
        try:
            result = await self.bridge.update()
            if result is not None:
                _LOGGER.debug(f"number of fields after query: {len(result)}")
            else:
                if self.bridge.should_be_refreshed():
                    _LOGGER.debug(f"we going to call async_refresh_with_pause() again")
                    try:
                        asyncio.create_task(self.async_refresh_with_pause())
                    except Exception as exc:
                        _LOGGER.debug(f"Exception while try to call 'asyncio.create_task(self.async_refresh_with_pause())': {exc}")

            return result

        except UpdateFailed as exception:
            raise UpdateFailed() from exception

        except Exception as other:
            _LOGGER.warning(f"unexpected: {other}")
            raise UpdateFailed() from other

    def clear_data(self):
        _LOGGER.debug(f"clear_data called...")
        self.data.clear()


async def async_unload_entry(hass: HomeAssistant, config_entry: ConfigEntry):
    unload_ok = await hass.config_entries.async_unload_platforms(config_entry, PLATFORMS)
    if unload_ok:
        if DOMAIN in hass.data and config_entry.entry_id in hass.data[DOMAIN]:
            hass.data[DOMAIN].pop(config_entry.entry_id)
    return unload_ok


async def async_reload_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> None:
    if await async_unload_entry(hass, config_entry):
        await asyncio.sleep(2)
        await async_setup_entry(hass, config_entry)


class TibberGraphApiEntity(Entity):
    _attr_should_poll = False
    _attr_has_entity_name = True
    _attr_name_addon = None

    def __init__(self, coordinator: TibberGraphApiDataUpdateCoordinator, description: EntityDescription) -> None:
        self.entity_description = description
        self.coordinator = coordinator
        self.entity_id = f"{DOMAIN}.{_camel_to_snake(self.coordinator._vehicle_name)}_{_camel_to_snake(description.key)}"

        if hasattr(description, "translation_key") and description.translation_key is not None:
            self._attr_translation_key = description.translation_key.lower()
        else:
            self._attr_translation_key = description.key.lower()

    # def __init__(self, coordinator: TibberGraphApiDataUpdateCoordinator, description: EntityDescription) -> None:
    #     self.tag = description.tag
    #     self.idx = None
    #     if hasattr(description, "idx") and description.idx is not None:
    #         self.idx = description.idx
    #     else:
    #         self.idx = None
    #
    #     if hasattr(description, "name_addon") and description.name_addon is not None:
    #         self._attr_name_addon = description.name_addon
    #
    #     if hasattr(description, "native_unit_of_measurement") and description.native_unit_of_measurement is not None:
    #         if "@@@" in description.native_unit_of_measurement:
    #             description.native_unit_of_measurement = description.native_unit_of_measurement.replace("@@@", coordinator._currency)

    @property
    def device_info(self) -> dict:
        return self.coordinator._device_info_dict

    @property
    def available(self):
        """Return True if entity is available."""
        return self.coordinator.last_update_success

    @property
    def unique_id(self):
        """Return a unique ID to use for this entity."""
        return self.entity_id

    async def async_added_to_hass(self):
        """Connect to dispatcher listening for entity data notifications."""
        self.async_on_remove(self.coordinator.async_add_listener(self.async_write_ha_state))

    async def async_update(self):
        """Update entity."""
        await self.coordinator.async_request_refresh()

    @property
    def should_poll(self) -> bool:
        return False


class TibberGraphApiBridge:
    # https://app.tibber.com/v4/gql

    DATA_URL = "https://app.tibber.com/v4/gql"
    LOGIN_URL = "https://app.tibber.com/login.credentials"
    REFRESH_URL = f"https://app.tibber.com/auth-sessions/{str(uuid.uuid4())}"

    REQ_HEADERS = {
        "Accept-Language": "en",
        "x-tibber-new-ui": "true",
        "User-Agent": "Tibber/24.46.0 (versionCode: 2446003Dalvik/2.1.0 (Linux; U; Android 11; sdk_gphone_x86_64 Build/RSR1.240422.006))",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    tibber_vehicleId = None
    tibber_vehicleName = None

    _require_refresh = False
    _the_refresh_token = None
    _web_session = None
    _user = None
    _pwd = None
    _veh_index = 0

    def __init__(self, user, pwd, a_web_session, veh_index: int = 0, veh_id: str = None, options: dict = None):
        if a_web_session is not None:
            _LOGGER.info(f"restarting TibberGraphApi integration... for tibber-vehicle-id: '{veh_id}' vehicle-index: '{veh_index}' with options: {options}")
            self._web_session = a_web_session
            self._user = user
            self._pwd = pwd
            self._veh_index = veh_index
            if veh_id is not None:
                self.tibber_vehicleId = veh_id

    async def update(self) -> dict:
        return await self.get_vehicle_data()

    def should_be_refreshed(self) -> bool:
        return self._require_refresh or "Authorization" not in self.REQ_HEADERS

    async def login(self) -> None:
        self.REQ_HEADERS["Content-Type"] = "application/x-www-form-urlencoded"
        login_data = f"email={self._user}&password={self._pwd}"
        async with self._web_session.post(self.LOGIN_URL, data=login_data, headers=self.REQ_HEADERS) as response:
            if response.status == 200:
                data = await response.json()

                # ok updating the headers
                self.REQ_HEADERS["Content-Type"] = "application/json; charset=utf-8"
                self.REQ_HEADERS["Authorization"] = data["token"]
                if "refreshToken" in data:
                    _LOGGER.debug(f"refreshToken received")
                    self._the_refresh_token = data["refreshToken"]
                    self._require_refresh = False
            else:
                self.REQ_HEADERS["Content-Type"] = "application/json; charset=utf-8"
                _LOGGER.warning(f"login {response.status} -> {response.reason}")

    async def refresh_token(self) -> None:
        if self._the_refresh_token is not None:
            self.REQ_HEADERS["Authorization"] = self._the_refresh_token
            self.REQ_HEADERS["Content-Type"] = "application/json; charset=utf-8"
            async with self._web_session.put(self.REFRESH_URL, headers=self.REQ_HEADERS) as response:
                if response.status == 200:
                    ref_data = None
                    ref_text = None
                    if response.headers["Content-Type"] == "application/json":
                        ref_data = await response.json()
                    else:
                        # we try to parse the text as json ?!
                        ref_text = await response.text()
                        try:
                            ref_data = json.loads(ref_text)
                        except Exception as other:
                            _LOGGER.warning(f"could not parse refresh response: {other} {ref_text}")

                    if ref_data is not None and "token" in ref_data:
                        self._require_refresh = False
                        self.REQ_HEADERS["Authorization"] = ref_data["token"]
                        if "refreshToken" in ref_data:
                            _LOGGER.debug(f"refreshToken updated !")
                            self._the_refresh_token = ref_data["refreshToken"]
                        else:
                            _LOGGER.warning(f"not refreshToken provided !")
                            self._the_refresh_token = None
                    else:
                        _LOGGER.warning(f"no valid data in refresh token response: {ref_data} {ref_text}")
                        self._require_refresh = False
                        self.REQ_HEADERS.pop("Authorization")
                else:
                    _LOGGER.warning(f"refresh_token: {response.status} -> {response.reason}")
                    self._require_refresh = False
                    self.REQ_HEADERS.pop("Authorization")
        else:
            _LOGGER.warning(f"refresh token was called but the 'refresh_token' is NONE")
            self._require_refresh = False
            self.REQ_HEADERS.pop("Authorization")

    async def get_vehicle_data(self) -> dict:
        if self._require_refresh:
            await self.refresh_token()

        if "Authorization" not in self.REQ_HEADERS:
            await self.login()

        if self.tibber_vehicleId is None or len(self.tibber_vehicleId) == 0:
            await self.get_vehicle_id()

        jdata = {
            "query": "query Query { me { vehicle(id: \"" + self.tibber_vehicleId + "\") { "
                     "isAlive isCharging chargingStatus smartChargingStatus hasConsumption enterPincode "
                     "battery { level estimatedRange canReadLevel } status { title description } "
                     "charging {sessionStartedAt targetedStateOfCharge chargerId progress {cost energy speed} } "
                     "userSettings { key value } "
                     "onboarding { status title cta { action enabled link text url } } "
                     "} } }"
        }

        async with self._web_session.post(self.DATA_URL, json=jdata, headers=self.REQ_HEADERS) as response:
            if response.status == 401:
                _LOGGER.debug(f"401 received - trying to refresh auth token")
                if self._the_refresh_token is None:
                    _LOGGER.warning(f"no refresh token available - wait for next call to re-login...")
                    self._require_refresh = False
                    self.REQ_HEADERS.pop("Authorization")
                else:
                    _LOGGER.debug(f"refresh token available... try to refresh next...")
                    self._require_refresh = True

            elif response.status == 200:
                data = await response.json()
                if "data" in data and "me" in data["data"] and "vehicle" in data["data"]["me"]:
                    return data["data"]["me"]["vehicle"]
            else:
                _LOGGER.warning(f"get_vehicle_data {response.status} -> {response.reason}")

            # if we haven't read any data (cause of 401 or other status) we return None
            return None

    async def get_vehicle_id(self) -> str:
        if "Authorization" not in self.REQ_HEADERS:
            await self.login()

        jdata = {
            "query": "query getVehicles {me {myVehicles {vehicles {id, title} } } }"
        }
        async with self._web_session.post(self.DATA_URL, json=jdata, headers=self.REQ_HEADERS) as response:
            if response.status == 200:
                data = await response.json()
                if "data" in data \
                        and "me" in data["data"] \
                        and "myVehicles" in data["data"]["me"] \
                        and "vehicles" in data["data"]["me"]["myVehicles"] \
                        and len(data["data"]["me"]["myVehicles"]["vehicles"]) > self._veh_index:
                    self.tibber_vehicleId = data["data"]["me"]["myVehicles"]["vehicles"][self._veh_index]["id"]
                    self.tibber_vehicleName = data["data"]["me"]["myVehicles"]["vehicles"][self._veh_index]["title"]
                else:
                    _LOGGER.warning(f"Could not find vehicle id in response: {data}")
            else:
                _LOGGER.warning(f"get_vehicle_id {response.status} -> {response.reason}")

    @property
    def vehicle_id(self):
        # if id is not here yet return None... but let's try to get it
        if self.tibber_vehicleId is None:
            self.get_vehicle_id()
            return None
        return self.tibber_vehicleId

    @property
    def vehicle_name(self):
        # if id is not here yet return None... but let's try to get it
        if self.tibber_vehicleName is None:
            self.get_vehicle_id()
            return None
        return self.tibber_vehicleName
