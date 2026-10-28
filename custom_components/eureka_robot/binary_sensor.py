"""Problem state from the verified work and station status tables."""

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)

from .entity import EurekaEntity


async def async_setup_entry(hass, entry, async_add_entities):
    async_add_entities(
        [
            EurekaProblem(entry.runtime_data, entry, "problem"),
            EurekaMop(entry.runtime_data, entry, "mop_installed"),
        ]
    )


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
