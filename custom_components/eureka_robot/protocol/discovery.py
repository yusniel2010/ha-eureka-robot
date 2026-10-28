"""Read-only discovery using real adapter prefixes and tolerant B8 probes."""

import asyncio
import ipaddress

from .client import EurekaClient
from .errors import EurekaError
from .transport import Transport

PRIVATE_NETWORKS = tuple(
    ipaddress.ip_network(cidr)
    for cidr in ("10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16")
)
MAX_NETWORK_ADDRESSES = 1024
MAX_SCAN_HOSTS = 4096


def parse_network(value: str) -> ipaddress.IPv4Network:
    network = ipaddress.ip_network(value.strip(), strict=False)
    if (
        network.version != 4
        or network.num_addresses > MAX_NETWORK_ADDRESSES
        or not any(network.subnet_of(private) for private in PRIVATE_NETWORKS)
    ):
        raise ValueError(
            "Use a private IPv4 network of at most 1024 addresses (/22 or smaller)"
        )
    return network


def networks_from_adapters(adapters: list[dict]) -> list[str]:
    """Search enabled private interfaces; bound huge corporate/VPN prefixes."""
    networks = []
    for adapter in sorted(adapters, key=lambda item: not item.get("default", False)):
        if not adapter.get("enabled"):
            continue
        for address in adapter.get("ipv4", []):
            try:
                ip = ipaddress.ip_address(address["address"])
                if ip.version != 4 or not any(
                    ip in private for private in PRIVATE_NETWORKS
                ):
                    continue
                prefix = int(address["network_prefix"])
                network = ipaddress.ip_network(f"{ip}/{prefix}", strict=False)
                if network.num_addresses > MAX_NETWORK_ADDRESSES:
                    network = ipaddress.ip_network(f"{ip}/24", strict=False)
            except (KeyError, TypeError, ValueError):
                continue
            if not any(network.subnet_of(existing) for existing in networks):
                networks = [
                    existing for existing in networks if not existing.subnet_of(network)
                ]
                networks.append(network)
    return [str(network) for network in networks]


async def probe_host(host: str):
    client = EurekaClient(host)
    # Robot sometimes closes a valid connection before replying. Retry those,
    # but do not spend three long attempts on every closed/nonexistent host.
    client.transport = Transport(
        host,
        attempts=3,
        timeout=1.5,
        connect_timeout=0.6,
        retry_connect_failures=False,
        accept_status_notify=True,
    )
    return await client.status()


async def discover_networks(values: list[str]) -> list[str]:
    hosts = {}
    for value in values:
        for ip in parse_network(value).hosts():
            hosts.setdefault(str(ip), None)
            if len(hosts) >= MAX_SCAN_HOSTS:
                break
        if len(hosts) >= MAX_SCAN_HOSTS:
            break
    semaphore = asyncio.Semaphore(32)

    async def probe(host):
        async with semaphore:
            try:
                await probe_host(host)
            except (EurekaError, OSError, TimeoutError):
                return None
            return host

    async with asyncio.TaskGroup() as group:
        tasks = [group.create_task(probe(host)) for host in hosts]
    return [host for task in tasks if (host := task.result()) is not None]


async def discover_network(value: str) -> list[str]:
    return await discover_networks([value])
