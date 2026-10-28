"""Expose only locally verified vacuum controls."""

from homeassistant.components.vacuum import (
    Segment,
    StateVacuumEntity,
    VacuumActivity,
    VacuumEntityFeature,
)
from homeassistant.exceptions import HomeAssistantError

from .entity import EurekaEntity
from .protocol.commands import FAN_LEVELS


PARALLEL_UPDATES = 1


async def async_setup_entry(hass, entry, async_add_entities):
    async_add_entities([EurekaVacuum(entry.runtime_data, entry)])


class EurekaVacuum(EurekaEntity, StateVacuumEntity):
    _attr_name = None
    _attr_supported_features = (
        VacuumEntityFeature.STATE
        | VacuumEntityFeature.START
        | VacuumEntityFeature.PAUSE
        | VacuumEntityFeature.STOP
        | VacuumEntityFeature.RETURN_HOME
        | VacuumEntityFeature.FAN_SPEED
        | VacuumEntityFeature.CLEAN_AREA
    )

    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry, "vacuum")

    @property
    def activity(self):
        value = self.coordinator.data.activity
        return VacuumActivity(value) if value else None

    async def async_pause(self):
        await self.coordinator.command("pause")

    async def async_stop(self, **kwargs):
        await self.coordinator.command("stop")

    @property
    def fan_speed_list(self):
        return list(FAN_LEVELS)

    @property
    def fan_speed(self):
        return next(
            (
                name
                for name, code in FAN_LEVELS.items()
                if code == self.coordinator.data.fan
            ),
            None,
        )

    @property
    def extra_state_attributes(self):
        return {
            **self._attr_extra_state_attributes,
            "rooms": self.coordinator.room_names(),
        }

    def _handle_coordinator_update(self):
        self._check_segments()
        super()._handle_coordinator_update()

    def _check_segments(self):
        """Ask the user to remap areas when the robot reports other rooms."""
        if self.registry_entry is None or not self.coordinator.rooms:
            return
        last_seen = self.last_seen_segments
        if last_seen is not None and {s.id for s in last_seen} != {
            str(room) for room in self.coordinator.rooms
        }:
            self.async_create_segments_issue()

    async def async_get_segments(self):
        return [
            Segment(id=str(room), name=f"Room {room}") for room in self.coordinator.rooms
        ]

    async def async_clean_segments(self, segment_ids, **kwargs):
        await self.coordinator.clean_rooms([int(s) for s in segment_ids], 1)

    async def async_start(self):
        if self.coordinator.data.has_task is None:
            raise HomeAssistantError(
                "Robot mission state is unknown; refresh status before starting"
            )
        await self.coordinator.command(
            "resume" if self.coordinator.data.has_task else "start"
        )

    async def async_return_to_base(self, **kwargs):
        await self.coordinator.command("dock")

    async def async_set_fan_speed(self, fan_speed, **kwargs):
        await self.coordinator.command("fan", fan_speed)

    async def async_clean_rooms(self, rooms, repeats=1):
        await self.coordinator.clean_rooms(rooms, repeats)
