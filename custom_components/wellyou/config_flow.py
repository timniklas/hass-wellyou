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

from .const import DOMAIN

class FitxConfigFlow(ConfigFlow, domain=DOMAIN):
    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._discovered_studios: dict[str, str] = {}

    async def async_step_user(self, formdata):
        websession = async_get_clientsession(self.hass)
        if formdata is not None:
            studioid = formdata[CONF_ID]
            await self.async_set_unique_id(f"wellyou-{studioid}", raise_on_progress=False)
            self._abort_if_unique_id_configured()
            
            try:
                async with websession.get(f"https://api.myfitapp.de/mob/homeScreen/{studioid}?w=1080&h=2058&appId=1150") as response:
                    response.raise_for_status()
                    response_json = await response.json()
                    screenid = 0
                    for tile in response_json['tiles']:
                        if tile['linkedModule'] != None and tile['linkedModule']['name'].startswith('Mein Studio'):
                            screenid = tile['linkedModule']['screenId']
                    
                    if screenid == 0:
                        return self.async_abort(reason="unknown")

                    async with websession.get(f"https://api.myfitapp.de/mob/screen/{screenid}?w=1080&h=2058") as response:
                        response.raise_for_status()
                        response_json = await response.json()
                        dataurl = ""
                        for tile in response_json['tiles']:
                            if tile['linkedModule'] != None and 'metricDataUrl' in tile['linkedModule']:
                                dataurl = tile['linkedModule']['metricDataUrl']
                        
                        if dataurl == "":
                            return self.async_abort(reason="unknown")

                        data = {}
                        data[CONF_ID] = dataurl.split('/')[-1]
                        data[CONF_NAME] = self._discovered_studios[studioid]
                        return self.async_create_entry(title=f"FitX {self._discovered_studios[studioid]}", data=data)

            except ClientResponseError as exc:
                return self.async_abort(reason="unknown")
            except ClientError as exc:
                return self.async_abort(reason="connenction")

        try:
            async with websession.get('https://api.myfitapp.de/json/klubSearch/wellyou?appid=1150') as response:
                response.raise_for_status()
                response_json = await response.json()
                for studio in response_json['klubJSONDTOList']:
                    name = studio['klubName']
                    branchId = studio['id']
                    self._discovered_studios[branchId] = name
        except ClientResponseError as exc:
            return self.async_abort(reason="unknown")
        except ClientError as exc:
            return self.async_abort(reason="connenction")

        return self.async_show_form(
            step_id="user", data_schema=vol.Schema(
                {vol.Required(CONF_ID): vol.In(self._discovered_studios)}
            ),
        )
