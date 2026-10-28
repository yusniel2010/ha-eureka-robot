"""Local Eureka robot integration."""

from pathlib import Path

import voluptuous as vol
from homeassistant.components.frontend import add_extra_js_url
from homeassistant.components.http import StaticPathConfig
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant
from homeassistant.helpers.service import async_register_platform_entity_service

from .const import DOMAIN, PLATFORMS
from .coordinator import EurekaCoordinator
from .frontend import CARD_PATH, CARD_URL, async_register_card_resource
from .protocol.client import EurekaClient


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Register actions and serve the bundled card once per HA process."""
    async_register_platform_entity_service(
        hass,
        DOMAIN,
        "clean_rooms",
        entity_domain="vacuum",
        schema={
            vol.Required("rooms"): vol.All(
                [vol.All(int, vol.Range(min=1, max=255))], vol.Length(min=1, max=10)
            ),
            vol.Optional("repeats", default=1): vol.All(int, vol.Range(min=1, max=3)),
        },
        func="async_clean_rooms",
    )
    url = CARD_PATH
    await hass.http.async_register_static_paths(
        [
            StaticPathConfig(
                url, str(Path(__file__).parent / "www/eureka-robot-card.js"), True
            )
        ]
    )
    await async_register_card_resource(hass)
    add_extra_js_url(hass, CARD_URL)
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    coordinator = EurekaCoordinator(hass, entry, EurekaClient(entry.data[CONF_HOST]))
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
