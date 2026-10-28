"""Serialize all requests to the robot's single-client port."""

import asyncio

from .commands import ROOMS, STATUS, clean_rooms_frame, command_frame
from .errors import EurekaCommandError, EurekaProtocolError
from .status import Status, decode_rooms, decode_status
from .transport import Transport


class EurekaClient:
    def __init__(self, host: str) -> None:
        self.transport = Transport(host)
        self._lock = asyncio.Lock()

    async def status(self) -> Status:
        async with self._lock:
            return decode_status(await self.transport.request(STATUS))

    async def rooms(self) -> dict[int, str]:
        async with self._lock:
            return decode_rooms(await self.transport.request(ROOMS))

    async def command(self, action: str, value=None) -> None:
        await self._set(command_frame(action, value))

    async def clean_rooms(self, rooms: list[int], repeats: int = 1, **settings) -> None:
        await self._set(clean_rooms_frame(rooms, repeats, **settings))

    async def _set(self, frame: bytes) -> None:
        async with self._lock:
            reply = await self.transport.request(frame)
        if len(reply) < 15:
            raise EurekaProtocolError("Truncated command acknowledgement")
        if reply[13] != 0:
            raise EurekaCommandError("Robot rejected command")
