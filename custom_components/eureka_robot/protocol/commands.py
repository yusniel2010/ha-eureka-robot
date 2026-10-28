"""B8 commands reconstructed from the official J15 panel's encoder tables.

Only the small operational subset is exposed. No reset, OTA or provisioning.
Table-derived features still need physical local-transport validation.
"""

from .errors import EurekaCommandError
from .frame import build_frame

FAN_LEVELS = {"off": 0, "soft": 1, "normal": 2, "high": 3, "low": 4, "max": 5}
CLEAN_MODES = {"vacuum_and_mop": 0, "vacuum": 1, "mop": 2, "vacuum_then_mop": 3}
ACTION_BODIES = {
    "start": "aa010104",
    "resume": "aa010106",
    "dock": "aa010101",
    "pause": "aa019900",
    "stop": "aa010107",
    "wash": "aa019901",
    "stop_washing": "aa019900",
    "station_clean": "aa015b01",
    "empty": "aa015a0201",
    "dry": "aa015c01",
    "stop_drying": "aa015c00",
}


def command_frame(action: str, value=None) -> bytes:
    if action in ACTION_BODIES:
        if value is not None:
            raise EurekaCommandError("This command takes no parameters")
        return build_frame(bytes.fromhex(ACTION_BODIES[action]))
    if action == "fan" and value in FAN_LEVELS:
        body = bytes((0xAA, 1, 0x50, FAN_LEVELS[value]))
    elif action == "mode" and value in CLEAN_MODES:
        body = bytes((0xAA, 1, 0x58, CLEAN_MODES[value]))
    elif (
        action == "water"
        and type(value) is int
        and (0 <= value <= 3 or 101 <= value <= 130)
    ):
        body = bytes((0xAA, 1, 0x51, value))
    else:
        raise EurekaCommandError("Unsupported command or parameter")
    return build_frame(body)


def clean_rooms_frame(
    rooms: list[int], repeats: int = 1, *, mode: int = 0, fan: int = 0, water: int = 0
) -> bytes:
    if (
        not isinstance(rooms, list)
        or not 1 <= len(rooms) <= 10
        or any(type(r) is not int or not 1 <= r <= 255 for r in rooms)
        or len(set(rooms)) != len(rooms)
        or type(repeats) is not int
        or not 1 <= repeats <= 3
        or type(mode) is not int
        or mode not in range(4)
        or type(fan) is not int
        or fan not in FAN_LEVELS.values()
        or type(water) is not int
        or not (0 <= water <= 3 or 1 <= water <= 30)
    ):
        raise EurekaCommandError("Invalid room cleaning parameters")
    # Same ten-record padding used by the official panel, including inactive rooms.
    body = bytearray((0xAA, 1, 3, 10))
    for room in rooms:
        body.extend((room, repeats, mode, 0, fan, water, 0, 0, 0, 0))
    body.extend(bytes((10 - len(rooms)) * 10))
    return build_frame(body)


STATUS = build_frame(bytes.fromhex("aa0101"), 3)
ROOMS = build_frame(bytes.fromhex("aa0228"), 3)
START = command_frame("start")
PAUSE = command_frame("pause")
STOP = command_frame("stop")
WASH = command_frame("wash")
STATION_CLEAN = command_frame("station_clean")
