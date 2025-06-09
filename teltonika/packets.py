"""Teltonika protocol packets and events."""

import struct
from dataclasses import dataclass

# Client packets.


@dataclass(frozen=True)
class LoginPacket:
    """Client connection request with IMEI."""

    data: bytearray


@dataclass(frozen=True)
class AVLPacket:
    """Client data event."""

    data: bytearray


# Server packets.


@dataclass(frozen=True)
class AcceptPacket:
    """Server accept packet."""

    code = b"\x01"


@dataclass(frozen=True)
class RejectPacket:
    """Server deny packet."""

    code = b"\x00"


@dataclass(frozen=True)
class AckPacket:
    """Server acknowledge packet."""

    num: int  # 4 bytes

    @property
    def code(self) -> bytes:
        return struct.pack(">B", self.num)


# Read events.


@dataclass
class NeedMoreData:
    """Need more data event."""


@dataclass
class CRC16CheckFailed:
    """Cyclic Redundancy Check failed event."""
