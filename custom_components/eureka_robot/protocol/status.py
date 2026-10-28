"""Decode offsets confirmed by the vendor's J15 control panel tables."""

from dataclasses import dataclass

from .errors import EurekaProtocolError

WORK_STATES = {
    1: "returning",
    2: "charging",
    3: "return_paused",
    4: "charged",
    5: "cleaning",
    6: "paused",
    7: "stopped",
    8: "updating",
    9: "fault",
    10: "sleeping",
    11: "relocating",
    12: "exploring",
    13: "washing",
    14: "washing",
    15: "wash_paused",
    16: "drying",
    17: "manual",
    18: "on_station",
    19: "cruising",
    20: "cruise_paused",
    21: "explore_paused",
    22: "finding_station",
    23: "location_reminder",
}
STATION_STATES = {
    0: "idle",
    1: "charging",
    2: "filling_water",
    3: "washing",
    4: "drying",
    5: "air_drying",
    6: "error",
    7: "charged",
    8: "sleeping",
    9: "self_cleaning",
    10: "emptying",
    11: "cutting_hair",
    12: "waiting_to_charge",
    13: "draining",
}


@dataclass(frozen=True)
class Status:
    work_status: int
    station_status: int
    battery: int | None
    fan: int
    water: int
    area: int | None = None
    clean_minutes: int | None = None
    has_mop: bool | None = None
    mop_mode: int | None = None
    robot_fault: str | None = None
    station_fault: str | None = None
    has_task: bool | None = False

    @property
    def activity(self) -> str | None:
        if self.work_status == 9 or self.station_status == 6:
            return "error"
        if self.work_status in (2, 4, 13, 14, 16, 18):
            return "docked"
        if self.work_status in (1, 22):
            return "returning"
        if self.work_status in (5, 11, 12, 19):
            return "cleaning"
        if self.work_status in (3, 6, 15, 20, 21):
            return "paused"
        if self.work_status in (7, 8, 10, 17, 23):
            return "idle"
        return None

    @property
    def active(self) -> bool:
        return self.activity in ("cleaning", "returning", "paused")


def decode_status(frame: bytes) -> Status:
    if (
        len(frame) < 49
        or frame[0] != 0xAA
        or frame[1] + 1 != len(frame)
        or frame[2] != 0xB8
        or sum(frame[1:]) & 0xFF
        or frame[9] not in (3, 4)
        or frame[10:13] != b"\xaa\x01\x01"
    ):
        raise EurekaProtocolError("Invalid status response")
    battery = frame[23]
    return Status(
        frame[13],
        frame[46],
        battery if battery <= 100 else None,
        frame[18],
        frame[20],
        area=frame[19] + ((frame[32] & 15) << 8),
        clean_minutes=frame[24] + ((frame[32] >> 4) << 8),
        has_mop=bool(frame[28] & 1),
        mop_mode=frame[44],
        robot_fault=f"{frame[26]:02x}{frame[27]:02x}"
        if frame[26] in (1, 2, 3, 255) and frame[27]
        else None,
        station_fault=f"ff{frame[45]:02x}" if frame[45] else None,
        has_task=frame[47] in (1, 2) if frame[47] in (0, 1, 2) else None,
    )


def decode_rooms(frame: bytes) -> dict[int, str]:
    """Local room IDs; names are cloud metadata and are never invented."""
    if (
        len(frame) < 15
        or frame[0] != 0xAA
        or len(frame) != frame[1] + 1
        or frame[2] != 0xB8
        or sum(frame[1:]) & 255
        or frame[9] != 3
        or frame[10] != 0xAA
        or frame[11] not in (1, 2)
        or frame[12] != 0x28
    ):
        raise EurekaProtocolError("Invalid room response")
    count = frame[13]
    if frame[11] == 1:
        stride, start = 5, 15
    else:
        if len(frame) < 17:
            raise EurekaProtocolError("Truncated room response")
        stride, start = frame[15] or 8, 16
    if stride < 5 or (count and start + count * stride > len(frame) - 1):
        raise EurekaProtocolError("Truncated or unsupported room list")
    return {
        room: f"Room {room}"
        for i in range(count)
        if (room := frame[start + i * stride]) != 0
    }
