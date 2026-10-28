"""Host lookups for a stable robot identity, without cloud or extra dependencies."""

import ipaddress
import re
import socket

from homeassistant.helpers.device_registry import format_mac

ARP_TABLE = "/proc/net/arp"
_MAC = re.compile(r"(?:[0-9a-f]{2}:){5}[0-9a-f]{2}")


def is_mac(value: str | None) -> bool:
    return bool(value) and bool(_MAC.fullmatch(value))


def mac_for_host(host: str, arp_table: str = ARP_TABLE) -> str | None:
    """Return the robot's MAC from the Linux ARP table (blocking).

    Only valid right after talking to the robot, which fills the ARP cache.
    """
    try:
        ip = str(ipaddress.ip_address(host))
    except ValueError:
        try:
            ip = socket.gethostbyname(host)
        except OSError:
            return None
    try:
        with open(arp_table, encoding="ascii") as table:
            next(table, None)
            for line in table:
                fields = line.split()
                if len(fields) >= 4 and fields[0] == ip and fields[3] != "00:00:00:00:00:00":
                    return format_mac(fields[3])
    except OSError:
        return None
    return None
