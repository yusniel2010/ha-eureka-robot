"""Local Eureka robot integration."""

from pathlib import Path

from homeassistant.components.frontend import add_extra_js_url
from homeassistant.components.http import StaticPathConfig
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant

from .const import DOMAIN, PLATFORMS, VERSION
from .coordinator import EurekaCoordinator
from .protocol.client import EurekaClient


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Serve the bundled card once per HA process."""
    url = f"/{DOMAIN}/eureka-robot-card.js"
    await hass.http.async_register_static_paths(
        [
            StaticPathConfig(
                url, str(Path(__file__).parent / "www/eureka-robot-card.js"), True
            )
        ]
    )
    add_extra_js_url(hass, f"{url}?v={VERSION}")
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    coordinator = EurekaCoordinator(hass, entry, EurekaClient(entry.data[CONF_HOST]))
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
