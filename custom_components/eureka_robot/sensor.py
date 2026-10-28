"""Verified B8 fields. Unknown codes retain their numeric value."""

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import PERCENTAGE, UnitOfArea, UnitOfTime

from .entity import EurekaEntity
from .protocol.status import ROBOT_FAULTS, STATION_FAULTS, STATION_STATES, WORK_STATES

FAULT_TABLES = {"robot_fault": ROBOT_FAULTS, "station_fault": STATION_FAULTS}


PARALLEL_UPDATES = 0


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
        elif key in FAULT_TABLES:
            self._attr_device_class = SensorDeviceClass.ENUM
            self._attr_options = sorted(
                {"none", "unknown", *FAULT_TABLES[key].values()}
            )

    @property
    def extra_state_attributes(self):
        attributes = dict(self._attr_extra_state_attributes)
        if self.key in FAULT_TABLES:
            attributes["code"] = getattr(self.coordinator.data, self.key)
        return attributes

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
        if self.key in FAULT_TABLES:
            code = getattr(status, self.key)
            return FAULT_TABLES[self.key].get(code, "unknown") if code else "none"
        return STATION_STATES.get(
            status.station_status, f"unknown_{status.station_status}"
        )
