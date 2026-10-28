"""Problem state from the verified work and station status tables."""

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)

from .entity import EurekaEntity
from .protocol.status import WATER_SHORTAGE


async def async_setup_entry(hass, entry, async_add_entities):
    async_add_entities(
        [
            EurekaProblem(entry.runtime_data, entry, "problem"),
            EurekaMop(entry.runtime_data, entry, "mop_installed"),
            EurekaWaterShortage(entry.runtime_data, entry, "water_shortage"),
        ]
    )


class EurekaWaterShortage(EurekaEntity, BinarySensorEntity):
    _attr_device_class = BinarySensorDeviceClass.PROBLEM
    _attr_translation_key = "water_shortage"
    _attr_icon = "mdi:water-off"

    @property
    def is_on(self):
        return self.coordinator.data.station_fault == WATER_SHORTAGE


class EurekaProblem(EurekaEntity, BinarySensorEntity):
    _attr_device_class = BinarySensorDeviceClass.PROBLEM
    _attr_translation_key = "problem"

    @property
    def is_on(self):
        return self.coordinator.data.activity == "error" or bool(
            self.coordinator.data.robot_fault or self.coordinator.data.station_fault
        )


class EurekaMop(EurekaEntity, BinarySensorEntity):
    _attr_translation_key = "mop_installed"
    _attr_icon = "mdi:robot-vacuum"

    @property
    def is_on(self):
        return self.coordinator.data.has_mop
