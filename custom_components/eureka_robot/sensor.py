"""Verified B8 fields. Unknown codes retain their numeric value."""

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import PERCENTAGE, UnitOfArea, UnitOfTime

from .entity import EurekaEntity
from .protocol.status import STATION_STATES, WORK_STATES


async def async_setup_entry(hass, entry, async_add_entities):
    async_add_entities(
        [
            EurekaSensor(entry.runtime_data, entry, key)
            for key in (
                "battery",
                "status",
                "station_status",
                "cleaned_area",
                "clean_time",
                "robot_fault",
                "station_fault",
            )
        ]
    )


class EurekaSensor(EurekaEntity, SensorEntity):
    def __init__(self, coordinator, entry, key):
        super().__init__(coordinator, entry, key)
        self.key = key
        self._attr_translation_key = key
        if key == "battery":
            self._attr_device_class = SensorDeviceClass.BATTERY
            self._attr_native_unit_of_measurement = PERCENTAGE
            self._attr_state_class = SensorStateClass.MEASUREMENT

        if key == "cleaned_area":
            self._attr_native_unit_of_measurement = UnitOfArea.SQUARE_METERS
        elif key == "clean_time":
            self._attr_native_unit_of_measurement = UnitOfTime.MINUTES
            self._attr_device_class = SensorDeviceClass.DURATION

    @property
    def native_value(self):
        status = self.coordinator.data
        if self.key == "battery":
            return status.battery
        if self.key == "status":
            return WORK_STATES.get(status.work_status, f"unknown_{status.work_status}")
        if self.key == "cleaned_area":
            return status.area
        if self.key == "clean_time":
            return status.clean_minutes
        if self.key == "robot_fault":
            return status.robot_fault or "none"
        if self.key == "station_fault":
            return status.station_fault or "none"
        return STATION_STATES.get(
            status.station_status, f"unknown_{status.station_status}"
        )
