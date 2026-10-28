"""Stable device and entity identity survives host reconfiguration."""

from homeassistant.helpers.device_registry import CONNECTION_NETWORK_MAC, DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .util import is_mac


class EurekaEntity(CoordinatorEntity):
    _attr_has_entity_name = True

    def __init__(self, coordinator, entry, key):
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_{key}"
        self._attr_extra_state_attributes = {"eureka_role": key}
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            connections={(CONNECTION_NETWORK_MAC, entry.unique_id)}
            if is_mac(entry.unique_id)
            else set(),
            name="Eureka J15 Pro Ultra",
            manufacturer="Eureka",
            model="J15 Pro Ultra",
        )
