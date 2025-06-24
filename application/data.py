"""Vehicle and records data objects."""

import asyncio
from dataclasses import dataclass

from framework.utils import AVLDataRecord


@dataclass
class Vehicle:
    """Data representation of a vehicle."""

    lat: float | None = None
    lng: float | None = None
    altitude: int | None = None
    angle: int | None = None
    speed: float | None = None

    @property
    def position(self) -> tuple[float, float] | None:
        """Position of the vehicle."""
        if self.lat and self.lng:
            return self.lat, self.lng
        return None


records: asyncio.Queue[AVLDataRecord] = asyncio.Queue(maxsize=300)
vehicle = Vehicle()
