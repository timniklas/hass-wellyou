from dataclasses import dataclass
from enum import StrEnum
import logging
from random import choice, randrange

from homeassistant.helpers.aiohttp_client import async_get_clientsession
from aiohttp import ClientError, ClientResponseError, ClientSession
from homeassistant.core import HomeAssistant

import json

_LOGGER = logging.getLogger(__name__)

class API:
    """Class for API."""

    def __init__(self, hass: HomeAssistant, studioid: int) -> None:
        """Initialise."""
        self.studioid = studioid
        self._session = async_get_clientsession(hass)
        self.connected: bool = False

    async def getLiveMetrics(self):
        """get map data from api."""

        try:
            async with self._session.get(f"https://cockpit.myfitapp.de/metric/get/{self.studioid}") as response:
                response.raise_for_status()
                response_json = await response.json()
                self.connected = True
                return response_json[0]['last']['dispPercent']
        except ClientError as exc:
            raise APIConnectionError("Unknown error.")


class APIConnectionError(Exception):
    """Exception class for connection error."""
