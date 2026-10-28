"""Cleaning mode and water controls from vendor protocol tables."""

from homeassistant.components.select import SelectEntity

from .entity import EurekaEntity
from .protocol.commands import CLEAN_MODES


PARALLEL_UPDATES = 1


async def async_setup_entry(hass, entry, async_add_entities):
    async_add_entities(
        [
            EurekaSelect(entry.runtime_data, entry, key)
            for key in ("clean_mode", "water_level")
        ]
        + [EurekaRoomSelect(entry.runtime_data, entry, "room")]
    )


class EurekaSelect(EurekaEntity, SelectEntity):
    def __init__(self, coordinator, entry, key):
        super().__init__(coordinator, entry, key)
        self.key = key
        self._attr_translation_key = key

    @property
    def options(self):
        if self.key == "clean_mode":
            return list(CLEAN_MODES)
        return (
            [str(n) for n in range(1, 31)]
            if self.coordinator.data.water >= 100
            else ["off", "low", "normal", "high"]
        )

    @property
    def current_option(self):
        status = self.coordinator.data
        if self.key == "clean_mode":
            return next(
                (k for k, v in CLEAN_MODES.items() if v == status.mop_mode), None
            )
        if status.water >= 100:
            return str(status.water - 100) if 101 <= status.water <= 130 else None
        return (
            ["off", "low", "normal", "high"][status.water]
            if 0 <= status.water <= 3
            else None
        )

    async def async_select_option(self, option):
        if self.key == "clean_mode":
            await self.coordinator.command("mode", option)
        else:
            value = (
                int(option) + 100
                if self.coordinator.data.water >= 100
                else ["off", "low", "normal", "high"].index(option)
            )
            await self.coordinator.command("water", value)


class EurekaRoomSelect(EurekaEntity, SelectEntity):
    """Pick one room for the Clean room button, to learn which ID is which."""

    _attr_translation_key = "room"
    _attr_icon = "mdi:floor-plan"

    @property
    def options(self):
        return list(self.coordinator.room_names().values())

    @property
    def current_option(self):
        return self.coordinator.room_names().get(self.coordinator.selected_room)

    async def async_select_option(self, option):
        self.coordinator.selected_room = next(
            room for room, name in self.coordinator.room_names().items() if name == option
        )
        self.async_write_ha_state()
