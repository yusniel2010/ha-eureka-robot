"""Poll local state and refresh optional room data without cloud access."""

import logging
import time
from datetime import timedelta

from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN
from .protocol.errors import EurekaError
from .protocol.status import Status

_LOGGER = logging.getLogger(__name__)
STATION_ACTIONS = {"wash", "station_clean", "empty", "dry", "stop_drying"}


class EurekaCoordinator(DataUpdateCoordinator[Status]):
    def __init__(self, hass, entry, client):
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            config_entry=entry,
            update_interval=timedelta(seconds=10),
        )
        self.client = client
        self.failures = 0
        self.rooms = {}
        self._rooms_updated = 0.0

    async def _async_update_data(self):
        try:
            status = await self.client.status()
        except EurekaError as err:
            self.failures += 1
            if self.failures >= 3 or self.data is None:
                raise UpdateFailed(str(err)) from err
            return self.data
        self.failures = 0
        finished = (
            self.data is not None
            and self.data.has_task is True
            and status.has_task is False
        )
        if time.monotonic() - self._rooms_updated >= 600 or finished:
            self._rooms_updated = time.monotonic()
            try:
                self.rooms = await self.client.rooms()
            except EurekaError:
                self.rooms = {}
                _LOGGER.debug("Optional local room query unavailable")
        self.update_interval = timedelta(
            seconds=3 if status.active or status.has_task else 10
        )
        return status

    async def command(self, action, value=None):
        if action in STATION_ACTIONS and self.data.activity != "docked":
            raise HomeAssistantError("Robot must be on the station")
        try:
            if value is None:
                await self.client.command(action)
            else:
                await self.client.command(action, value)
        except EurekaError as err:
            await self.async_request_refresh()
            raise HomeAssistantError(str(err)) from err
        await self.async_request_refresh()

    async def clean_rooms(self, rooms, repeats):
        if not self.rooms or any(room not in self.rooms for room in rooms):
            raise HomeAssistantError("Select rooms from the current local room list")
        status = self.data
        if status.mop_mode is None or status.mop_mode not in range(4):
            raise HomeAssistantError("Choose a supported cleaning mode first")
        water = status.water - 100 if status.water >= 100 else status.water
        try:
            await self.client.clean_rooms(
                rooms, repeats, mode=status.mop_mode, fan=status.fan, water=water
            )
        except EurekaError as err:
            await self.async_request_refresh()
            raise HomeAssistantError(str(err)) from err
        await self.async_request_refresh()
