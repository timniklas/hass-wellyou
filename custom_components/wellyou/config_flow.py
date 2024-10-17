import voluptuous as vol
from homeassistant.config_entries import ConfigFlow
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from aiohttp import ClientError, ClientResponseError, ClientSession
import json

from homeassistant.helpers.selector import selector

from homeassistant.const import (
    CONF_ID,
    CONF_NAME
)

from .const import (
    DOMAIN,
    STUDIOS
)

class MyfitappConfigFlow(ConfigFlow, domain=DOMAIN):
    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""

    async def async_step_user(self, formdata):
        websession = async_get_clientsession(self.hass)
        if formdata is not None:
            studio_id = formdata[CONF_ID]
            studio_name = STUDIOS[studio_id]
            await self.async_set_unique_id("myfitapp-" + studio_name.replace(' ', '-'), raise_on_progress=False)
            self._abort_if_unique_id_configured()
            data = {}
            data[CONF_ID] = studio_id
            data[CONF_NAME] = studio_name
            return self.async_create_entry(title=studio_name, data=data)

        return self.async_show_form(
            step_id="user", data_schema=vol.Schema(
                {vol.Required(CONF_ID): vol.In(STUDIOS)}
            ),
        )
