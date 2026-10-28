"""Register the bundled dashboard module without manual resource setup."""

from homeassistant.components.lovelace.const import LOVELACE_DATA
from homeassistant.components.lovelace.resources import ResourceStorageCollection
from homeassistant.core import HomeAssistant

from .const import DOMAIN, VERSION

CARD_PATH = f"/{DOMAIN}/eureka-robot-card.js"
CARD_URL = f"{CARD_PATH}?v={VERSION}"


async def async_register_card_resource(hass: HomeAssistant) -> None:
    """Persist in storage mode; YAML mode uses the frontend extra-module loader."""
    resources = hass.data[LOVELACE_DATA].resources
    if not isinstance(resources, ResourceStorageCollection):
        return
    if not resources.loaded:
        await resources.async_load()
        resources.loaded = True
    for item in resources.async_items():
        if item["url"].split("?", 1)[0] == CARD_PATH:
            if item["url"] != CARD_URL or item["type"] != "module":
                await resources.async_update_item(
                    item["id"], {"url": CARD_URL, "res_type": "module"}
                )
            return
    await resources.async_create_item({"url": CARD_URL, "res_type": "module"})
