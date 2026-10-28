"""Poll local state and refresh optional room data without cloud access."""

import asyncio
import logging
import time
from datetime import timedelta

from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN
from .protocol.commands import CLEAN_MODES, FAN_LEVELS
from .protocol.errors import EurekaError, EurekaOutcomeUnknownError
from .protocol.status import WATER_SHORTAGE, Status

_LOGGER = logging.getLogger(__name__)
STATION_ACTIONS = {"wash", "stop_washing", "station_clean", "empty", "dry", "stop_drying"}
RECHECK_INTERVAL = 2
RECHECK_ATTEMPTS = 15


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
        before = self.data
        try:
            if value is None:
                await self.client.command(action)
            else:
                await self.client.command(action, value)
        except EurekaOutcomeUnknownError as err:
            if await self._confirm_outcome(action, value, before):
                return
            await self.async_request_refresh()
            raise HomeAssistantError(str(err)) from err
        except EurekaError as err:
            await self.async_request_refresh()
            raise HomeAssistantError(str(err)) from err
        await self.async_request_refresh()

    async def _confirm_outcome(self, action, value, before):
        """Read back a changed target state; never resend an uncertain command."""
        try:
            async with asyncio.timeout(8):
                for attempt in range(3):
                    if attempt:
                        await asyncio.sleep(1)
                    try:
                        after = await self.client.status()
                    except EurekaError:
                        continue
                    self.failures = 0
                    self.update_interval = timedelta(
                        seconds=3 if after.active or after.has_task else 10
                    )
                    self.async_set_updated_data(after)
                    if _observed_transition(action, value, before, after):
                        _LOGGER.debug(
                            "Command %s verified by status transition after missing acknowledgement",
                            action,
                        )
                        return True
        except TimeoutError:
            pass
        _LOGGER.debug(
            "Command %s could not be verified after missing acknowledgement", action
        )
        return False

    async def recheck_water(self):
        """Clear a latched empty-tank alert after refilling.

        The station only re-reads the tank when it pumps water, so start a mop
        wash, wait for the alert to clear, then stop washing at once.
        """
        if self.data.activity != "docked":
            raise HomeAssistantError("Robot must be on the station")
        await self.command("wash")
        try:
            status = await self._wait_for_water_check()
        finally:
            await self.command("stop_washing")
        if status is None or status.station_fault == WATER_SHORTAGE:
            raise HomeAssistantError("Clean water tank still reports empty")

    async def _wait_for_water_check(self):
        status = None
        for _ in range(RECHECK_ATTEMPTS):
            try:
                status = await self.client.status()
            except EurekaError:
                await asyncio.sleep(RECHECK_INTERVAL)
                continue
            self.async_set_updated_data(status)
            if status.station_fault != WATER_SHORTAGE:
                return status
            await asyncio.sleep(RECHECK_INTERVAL)
        return status

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


def _observed_transition(action, value, before, after):
    """Require a new reported target state, not a pre-existing condition."""

    if action not in ("fan", "water", "mode") and (
        after.activity == "error" or after.robot_fault or after.station_fault
    ):
        return False

    def target(status):
        if action == "wash":
            return status.station_status == 3 or status.work_status in (13, 14)
        if action == "stop_washing":
            return status.station_status != 3 and status.work_status not in (13, 14)
        if action == "station_clean":
            return status.station_status == 9
        if action == "empty":
            return status.station_status == 10
        if action == "dry":
            return status.station_status in (4, 5) or status.work_status == 16
        if action == "fan":
            return status.fan == FAN_LEVELS.get(value)
        if action == "water":
            return status.water == value
        if action == "mode":
            return status.mop_mode == CLEAN_MODES.get(value)
        if action == "start":
            return status.has_task is True
        if action == "resume":
            return status.activity == "cleaning" and status.has_task is True
        if action == "pause":
            return status.activity == "paused"
        if action == "stop":
            return status.has_task is False and status.activity in ("idle", "docked")
        if action == "dock":
            return status.activity in ("returning", "docked")
        return False

    return not target(before) and target(after)
