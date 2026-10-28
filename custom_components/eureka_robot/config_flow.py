"""Configure a local robot without a cloud account."""

import ipaddress
import re

import voluptuous as vol
from homeassistant.components import network
from homeassistant.config_entries import ConfigFlow
from homeassistant.const import CONF_HOST

from .const import DOMAIN
from .protocol.client import EurekaClient
from .protocol.discovery import discover_network, parse_network
from .protocol.errors import EurekaError


def normalize_host(value: str) -> str:
    host = value.strip().lower().rstrip(".")
    try:
        return str(ipaddress.ip_address(host))
    except ValueError:
        if (
            len(host) > 253
            or not host
            or any(
                not re.fullmatch(r"[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?", part)
                for part in host.split(".")
            )
        ):
            raise ValueError("Enter an IP address or hostname") from None
        return host


class EurekaConfigFlow(ConfigFlow, domain=DOMAIN):
    VERSION = 1

    def __init__(self):
        self._scan_task = None
        self._candidates = []
        self._scan_network = ""

    async def async_step_scan(self, user_input=None):
        errors = {}
        if user_input:
            try:
                parse_network(user_input["network"])
            except ValueError:
                errors["network"] = "invalid_network"
            else:
                self._scan_network = user_input["network"]
                self._scan_task = self.hass.async_create_background_task(
                    discover_network(self._scan_network), "Eureka LAN discovery"
                )
                return await self.async_step_scan_progress()
        if not self._scan_network:
            for adapter in await network.async_get_adapters(self.hass):
                if adapter["enabled"]:
                    for address in adapter["ipv4"]:
                        ip = ipaddress.ip_address(address["address"])
                        if ip.is_private and not ip.is_loopback:
                            self._scan_network = str(
                                ipaddress.ip_network(f"{ip}/24", strict=False)
                            )
                            break
                    if self._scan_network:
                        break
        return self.async_show_form(
            step_id="scan",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        "network", default=self._scan_network or "192.168.1.0/24"
                    ): str
                }
            ),
            errors=errors,
        )

    async def async_step_scan_progress(self, user_input=None):
        if self._scan_task.done():
            try:
                self._candidates = self._scan_task.result()
            except (OSError, ValueError):
                self._candidates = []
            configured = {e.data[CONF_HOST] for e in self._async_current_entries()}
            self._candidates = [
                host for host in self._candidates if host not in configured
            ]
            return self.async_show_progress_done(
                next_step_id="choose_device" if self._candidates else "no_devices"
            )
        return self.async_show_progress(
            step_id="scan_progress",
            progress_action="scanning",
            progress_task=self._scan_task,
        )

    async def async_step_no_devices(self, user_input=None):
        return self.async_show_menu(
            step_id="no_devices", menu_options=["scan", "manual"]
        )

    async def async_step_choose_device(self, user_input=None):
        errors = {}
        if user_input:
            if not user_input.get("confirm_model"):
                errors["base"] = "confirm_model"
            elif user_input.get(CONF_HOST) not in self._candidates:
                errors["base"] = "cannot_connect"
            else:
                result = await self._form("user", {CONF_HOST: user_input[CONF_HOST]})
                if result["type"] != "form":
                    return result
                errors = result.get("errors", {})
        return self.async_show_form(
            step_id="choose_device",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_HOST): vol.In(self._candidates),
                    vol.Required("confirm_model", default=False): bool,
                }
            ),
            errors=errors,
        )

    async def async_step_manual(self, user_input=None):
        return await self._form("manual", user_input)

    async def _form(self, step_id, user_input):
        errors = {}
        entry = self._get_reconfigure_entry() if step_id == "reconfigure" else None
        if user_input is not None:
            try:
                host = normalize_host(user_input[CONF_HOST])
            except ValueError:
                errors[CONF_HOST] = "invalid_host"
            else:
                for configured in self._async_current_entries():
                    if (
                        configured.entry_id != (entry.entry_id if entry else None)
                        and configured.data[CONF_HOST] == host
                    ):
                        return self.async_abort(reason="already_configured")
                try:
                    await EurekaClient(host).status()
                except (EurekaError, OSError, TimeoutError):
                    errors["base"] = "cannot_connect"
                else:
                    if entry:
                        return self.async_update_reload_and_abort(
                            entry, data_updates={CONF_HOST: host}, unique_id=host
                        )
                    await self.async_set_unique_id(host)
                    self._abort_if_unique_id_configured()
                    return self.async_create_entry(
                        title="Eureka J15 Pro Ultra", data={CONF_HOST: host}
                    )
        default = entry.data[CONF_HOST] if entry else ""
        return self.async_show_form(
            step_id=step_id,
            data_schema=vol.Schema({vol.Required(CONF_HOST, default=default): str}),
            errors=errors,
        )

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            return await self._form("user", user_input)
        return self.async_show_menu(step_id="user", menu_options=["scan", "manual"])

    async def async_step_reconfigure(self, user_input=None):
        return await self._form("reconfigure", user_input)
