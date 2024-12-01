import logging

import voluptuous as vol
from aiohttp import ClientResponseError
from homeassistant import config_entries
from homeassistant.const import CONF_NAME, CONF_SCAN_INTERVAL, CONF_USERNAME, CONF_PASSWORD
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from requests.exceptions import HTTPError, Timeout

from custom_components.tibber_graphapi import TibberGraphApiBridge
from .const import (
    DOMAIN,
    CONF_VEHINDEX_NUMBER,
    CONF_TIBBER_VEHICLE_ID,
    CONF_TIBBER_VEHICLE_NAME,

    DEFAULT_CONF_NAME,
    DEFAULT_USERNAME,
    DEFAULT_PWD,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_VEHINDEX_NUMBER
)

_LOGGER = logging.getLogger(__name__)


@staticmethod
def tibber_graphapi_entries(hass: HomeAssistant):
    conf_hosts = []

    for entry in hass.config_entries.async_entries(DOMAIN):
        if hasattr(entry, 'options') and CONF_TIBBER_VEHICLE_ID in entry.options:
            conf_hosts.append(entry.options[CONF_TIBBER_VEHICLE_ID])
        else:
            conf_hosts.append(entry.data[CONF_TIBBER_VEHICLE_ID])

    return conf_hosts


@staticmethod
def _host_in_configuration_exists(veh_id: str, hass: HomeAssistant) -> bool:
    if veh_id in tibber_graphapi_entries(hass):
        return True
    return False


class TibberLocalConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    def __init__(self):
        self._errors = {}

    async def _test_connection_tibber_graphapi(self, user, pwd, veh_idx) -> bool:
        self._errors = {}
        try:
            bridge = TibberGraphApiBridge(user=user, pwd=pwd, websession=async_get_clientsession(self.hass), veh_index=veh_idx)
            try:
                await bridge.get_vehicle_id()
                self._tibber_veh_id = bridge.vehicle_id
                self._tibber_veh_name = bridge.vehicle_name
                return True

            except ValueError as val_err:
                self._errors[CONF_USERNAME] = "unknown_mode"
                _LOGGER.warning(f"ValueError: {val_err}")

        except (OSError, HTTPError, Timeout, ClientResponseError):
            self._errors[CONF_USERNAME] = "cannot_connect"
            _LOGGER.warning("Could not connect to your Tibber account [%s] or no vehicle found at given index", user)
        return False

    async def async_step_user(self, user_input=None):
        self._errors = {}
        if user_input is not None:
            user = user_input.get(CONF_USERNAME, DEFAULT_USERNAME).lower()
            pwd = user_input.get(CONF_PASSWORD, "")
            veh_idx = user_input.get(CONF_VEHINDEX_NUMBER, DEFAULT_VEHINDEX_NUMBER)

            if await self._test_connection_tibber_graphapi(user, pwd, veh_idx):
                if _host_in_configuration_exists(self._tibber_veh_id, self.hass):
                    self._errors[CONF_USERNAME] = "already_configured"
                else:
                    scan = user_input.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
                    name = f"{user_input.get(CONF_NAME, f"{DEFAULT_CONF_NAME}")} {self._tibber_veh_name}"
                    a_data = {CONF_NAME: name,
                              CONF_USERNAME: user,
                              CONF_PASSWORD: pwd,
                              CONF_SCAN_INTERVAL: scan,
                              CONF_VEHINDEX_NUMBER: veh_idx,
                              CONF_TIBBER_VEHICLE_NAME: self._tibber_veh_name,
                              CONF_TIBBER_VEHICLE_ID: self._tibber_veh_id}

                    return self.async_create_entry(title=name, data=a_data)
            else:
                _LOGGER.error("Could not connect to your Tibber account [%s]", user)
        else:
            user_input = {}
            user_input[CONF_NAME] = DEFAULT_CONF_NAME
            user_input[CONF_USERNAME] = DEFAULT_USERNAME
            user_input[CONF_PASSWORD] = DEFAULT_PWD
            user_input[CONF_SCAN_INTERVAL] = DEFAULT_SCAN_INTERVAL
            user_input[CONF_VEHINDEX_NUMBER] = DEFAULT_VEHINDEX_NUMBER

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_NAME, default=user_input.get(CONF_NAME, DEFAULT_CONF_NAME)
                    ): str,
                    vol.Required(
                        CONF_USERNAME, default=user_input.get(CONF_USERNAME, DEFAULT_USERNAME)
                    ): str,
                    vol.Required(
                        CONF_PASSWORD, default=user_input.get(CONF_PASSWORD, DEFAULT_PWD)
                    ): str,
                    vol.Required(
                        CONF_SCAN_INTERVAL, default=user_input.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
                    ): int,
                    vol.Required(
                        CONF_VEHINDEX_NUMBER, default=user_input.get(CONF_VEHINDEX_NUMBER, DEFAULT_VEHINDEX_NUMBER)
                    ): int,
                }
            ),
            last_step=True,
            errors=self._errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return TibberLocalOptionsFlowHandler(config_entry)


class TibberLocalOptionsFlowHandler(config_entries.OptionsFlow):

    def __init__(self, config_entry):
        """Initialize HACS options flow."""
        self.data = dict(config_entry.data);
        if len(dict(config_entry.options)) == 0:
            self.options = {}
        else:
            self.options = dict(config_entry.options)

    async def async_step_init(self, user_input=None):  # pylint: disable=unused-argument
        """Manage the options."""
        return await self.async_step_user()

    async def async_step_user(self, user_input=None):
        self._errors = {}
        if user_input is not None:
            self.options.update(user_input)
            return self._update_options()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_NAME,
                             default=self.options.get(CONF_NAME, self.data.get(CONF_NAME, DEFAULT_CONF_NAME))): str,
                vol.Required(CONF_USERNAME,
                             default=self.options.get(CONF_USERNAME, self.data.get(CONF_USERNAME, DEFAULT_USERNAME))): str,
                vol.Required(CONF_PASSWORD,
                             default=self.options.get(CONF_PASSWORD, self.data.get(CONF_PASSWORD, DEFAULT_PWD))): str,
                vol.Required(CONF_SCAN_INTERVAL, default=self.options.get(CONF_SCAN_INTERVAL,
                                                                          self.data.get(CONF_SCAN_INTERVAL,
                                                                                        DEFAULT_SCAN_INTERVAL))): int,
            }),
        )

    def _update_options(self):
        """Update config entry options."""
        return self.async_create_entry(data=self.options)
