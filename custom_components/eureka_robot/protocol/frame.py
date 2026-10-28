"""Midea UART framing with incremental validation."""

from .errors import EurekaProtocolError


def build_frame(body: bytes, msg_type: int = 2) -> bytes:
    if not 3 <= len(body) <= 245 or msg_type not in (2, 3, 4):
        raise EurekaProtocolError("Invalid B8 body or message type")
    data = bytearray([0xAA, len(body) + 10, 0xB8, 0, 0, 0, 0, 0, 0, msg_type])
    data.extend(body)
    data.append(-sum(data[1:]) & 0xFF)
    return bytes(data)


class FrameParser:
    """Buffer split packets, discard noise and invalid checksums."""

    def __init__(self) -> None:
        self.buffer = bytearray()

    def feed(self, data: bytes) -> list[bytes]:
        self.buffer.extend(data)
        frames = []
        while self.buffer:
            if self.buffer[0] != 0xAA:
                del self.buffer[0]
                continue
            if len(self.buffer) < 3:
                break
            length = self.buffer[1] + 1
            if length < 14 or self.buffer[2] != 0xB8:
                del self.buffer[0]
                continue
            if len(self.buffer) < length:
                break
            frame = bytes(self.buffer[:length])
            if sum(frame[1:]) & 0xFF:
                del self.buffer[0]
                continue
            del self.buffer[:length]
            frames.append(frame)
        return frames
