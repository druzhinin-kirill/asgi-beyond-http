"""Vehicle and records data objects."""

import asyncio
from dataclasses import dataclass

from framework.utils import AVLDataRecord


@dataclass
class Vehicle:
    lat: float | None = None
    lng: float | None = None
    altitude: int | None = None
    angle: int | None = None
    speed: float | None = None

    @property
    def position(self) -> tuple[float, float]:
        return self.lat, self.lng


records: asyncio.Queue[AVLDataRecord] = asyncio.Queue(maxsize=300)
vehicle = Vehicle()
