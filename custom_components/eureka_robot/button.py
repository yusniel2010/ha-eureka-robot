"""Station controls derived from the official panel encoder."""

from homeassistant.components.button import ButtonEntity

from .entity import EurekaEntity

ACTIONS = {
    "wash_mops": ("wash", "mdi:water-sync"),
    "empty_dust": ("empty", "mdi:delete-empty"),
    "dry_mops": ("dry", "mdi:weather-windy"),
    "stop_drying": ("stop_drying", "mdi:fan-off"),
    "clean_station": ("station_clean", "mdi:shower-head"),
    "check_water": ("recheck_water", "mdi:water-check"),
}


async def async_setup_entry(hass, entry, async_add_entities):
    async_add_entities(
        [EurekaStationButton(entry.runtime_data, entry, key) for key in ACTIONS]
    )


class EurekaStationButton(EurekaEntity, ButtonEntity):
    def __init__(self, coordinator, entry, key):
        super().__init__(coordinator, entry, key)
        self._attr_translation_key = key
        self.action, self._attr_icon = ACTIONS[key]

    @property
    def available(self):
        return super().available and self.coordinator.data.activity == "docked"

    async def async_press(self):
        if self.action == "recheck_water":
            await self.coordinator.recheck_water()
            return
        await self.coordinator.command(self.action)
