"""Framework utils.

This module provides abstraction over ASGI events. Instead of
exposing bare ASGI events, framework processes them into
user-friendly pythonic objects with decoded fields.

This way, target applications can focus purely on the
application business logic.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Self

from framework.byte_reader import ByteReader


@dataclass
class Login:
    """Teltonika login packet."""

    imei: str

    @classmethod
    def from_bytes(cls, b: bytearray) -> Self:
        return cls(imei=b.decode())


@dataclass
class AVLDataRecord:
    """Teltonika data record."""

    timestamp: str
    priority: int
    latitude: float
    longitude: float
    altitude: int
    angle: int
    satellites: int
    speed: int
    event_id: int
    io_element_count: int
    io_elements: list[dict[str, Any]]

    @classmethod
    def from_stream(cls, stream: ByteReader) -> "AVLDataRecord":
        ts = stream.read_u64()
        timestamp = datetime.fromtimestamp(ts / 1000).isoformat()

        priority = stream.read_u8()
        latitude = stream.read_i32() / 10_000_000
        longitude = stream.read_i32() / 10_000_000
        altitude = stream.read_i16()
        angle = stream.read_i16()
        satellites = stream.read_u8()
        speed = stream.read_u16()
        event_id = stream.read_u8()
        total_io = stream.read_u8()

        io_elements = []
        for _ in range(total_io):
            io_id = stream.read_u8()
            io_type = stream.read_u8()

            if io_type == 0x01:  # Digital (1 byte)
                io_value = stream.read_u8()
            elif io_type == 0x02:  # Analog (2 bytes)
                io_value = stream.read_u16()
            elif io_type == 0x03:  # Extended (4 bytes)
                io_value = stream.read_u32()
            else:
                io_value = None  # или raise ValueError

            io_elements.append(
                {
                    "io_id": io_id,
                    "io_type": io_type,
                    "io_value": io_value,
                }
            )

        return cls(
            timestamp=timestamp,
            priority=priority,
            latitude=latitude,
            longitude=longitude,
            altitude=altitude,
            angle=angle,
            satellites=satellites,
            speed=speed,
            event_id=event_id,
            io_element_count=total_io,
            io_elements=io_elements,
        )


@dataclass
class AVLData:
    """Teltonika data packet."""

    codec: int
    record_count: int
    records: list[AVLDataRecord]

    @classmethod
    def from_bytes(cls, b: bytearray) -> Self:
        stream = ByteReader(b)
        codec = stream.read_u8()
        record_count = stream.read_u8()
        records = [AVLDataRecord.from_stream(stream) for _ in range(record_count)]
        return cls(codec=codec, record_count=record_count, records=records)


@dataclass
class AVLDataResponse:
    """Teltonika response data packet."""

    num: int = 0
