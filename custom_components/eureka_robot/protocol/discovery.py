"""Explicit bounded LAN scan; never sends a control command."""

import asyncio
import ipaddress

from .client import EurekaClient
from .errors import EurekaError
from .transport import Transport

PRIVATE_NETWORKS = tuple(
    ipaddress.ip_network(cidr)
    for cidr in ("10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16")
)


def parse_network(value: str) -> ipaddress.IPv4Network:
    network = ipaddress.ip_network(value.strip(), strict=False)
    if (
        network.version != 4
        or network.num_addresses > 256
        or not any(network.subnet_of(private) for private in PRIVATE_NETWORKS)
    ):
        raise ValueError(
            "Use a private IPv4 network of at most 256 addresses (/24 or smaller)"
        )
    return network


async def probe_host(host: str):
    client = EurekaClient(host)
    client.transport = Transport(host, attempts=1, timeout=0.6)
    return await client.status()


async def discover_network(value: str) -> list[str]:
    network = parse_network(value)
    semaphore = asyncio.Semaphore(16)

    async def probe(ip):
        async with semaphore:
            try:
                await probe_host(str(ip))
            except (EurekaError, OSError, TimeoutError):
                return None
            return str(ip)

    # TaskGroup cancellation closes all pending sockets when the flow is removed.
    async with asyncio.TaskGroup() as group:
        tasks = [group.create_task(probe(ip)) for ip in network.hosts()]
    return [host for task in tasks if (host := task.result()) is not None]
