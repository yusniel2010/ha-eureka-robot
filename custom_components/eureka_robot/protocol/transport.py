"""Short-lived local TCP requests; send immediately after connecting."""

import asyncio
import logging
import random

from .errors import EurekaConnectionError, EurekaOutcomeUnknownError
from .frame import FrameParser

_LOGGER = logging.getLogger(__name__)


class Transport:
    def __init__(
        self,
        host: str,
        port: int = 12127,
        *,
        attempts: int = 3,
        timeout: float = 2,
        connect_timeout: float | None = None,
        retry_connect_failures: bool = True,
        accept_status_notify: bool = False,
    ) -> None:
        self.host = host
        self.port = port
        self.attempts = attempts
        self.timeout = timeout
        self.connect_timeout = timeout if connect_timeout is None else connect_timeout
        self.retry_connect_failures = retry_connect_failures
        self.accept_status_notify = accept_status_notify

    async def request(self, frame: bytes) -> bytes:
        last_error = None
        for attempt in range(self.attempts):
            writer = None
            sent = False
            received_bytes = 0
            received_frames = 0
            try:
                async with asyncio.timeout(self.connect_timeout):
                    reader, writer = await asyncio.open_connection(self.host, self.port)
                    sent = True
                    _LOGGER.debug("B8 TX attempt=%d frame=%s", attempt + 1, frame.hex())
                    writer.write(frame)
                    await writer.drain()
                parser = FrameParser()
                async with asyncio.timeout(self.timeout):
                    while data := await reader.read(4096):
                        received_bytes += len(data)
                        _LOGGER.debug("B8 RX chunk=%s", data[:256].hex())
                        for reply in parser.feed(data):
                            received_frames += 1
                            _LOGGER.debug("B8 RX valid frame=%s", reply.hex())
                            if (
                                reply[9] == frame[9]
                                or (
                                    self.accept_status_notify
                                    and frame[9] == 3
                                    and reply[9] == 4
                                    and frame[10:13] == b"\xaa\x01\x01"
                                )
                            ) and (
                                reply[10:13] == frame[10:13]
                                or (
                                    frame[9] == 3
                                    and frame[10:13] == b"\xaa\x02\x28"
                                    and reply[10] == 0xAA
                                    and reply[11] in (1, 2)
                                    and reply[12] == 0x28
                                )
                            ):
                                return reply
                last_error = "Connection closed before matching response"
            except (OSError, TimeoutError) as err:
                last_error = type(err).__name__
            finally:
                if writer is not None:
                    writer.close()
                    try:
                        async with asyncio.timeout(0.5):
                            await writer.wait_closed()
                    except (OSError, TimeoutError):
                        pass
            if sent and frame[9] == 2:
                raise EurekaOutcomeUnknownError(
                    "Command outcome is unknown; "
                    f"{last_error}; received={received_bytes} bytes, valid_frames={received_frames}. "
                    "Inspect robot status before retrying"
                )
            if not sent and not self.retry_connect_failures:
                break
            if attempt < self.attempts - 1:
                await asyncio.sleep(random.uniform(0.3, 0.8))
        raise EurekaConnectionError(f"No response from robot ({last_error})")
