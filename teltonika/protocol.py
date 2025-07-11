"""Implement Teltonika to process incoming bytes to events."""

import logging
from enum import StrEnum
from typing import TypeAlias

from teltonika.packets import AVLPacket, CRC16CheckFailed, LoginPacket, NeedMoreData

LOGGER = logging.getLogger(__name__)

ProtocolEvent: TypeAlias = LoginPacket | AVLPacket | CRC16CheckFailed | NeedMoreData


class ProtocolState(StrEnum):
    """Teltonika server protocol states."""

    LOGIN = "LOGIN"
    DATA = "DATA"


class Teltonika:
    """Translate incoming bytes to events."""

    def __init__(self):
        """Initialize empty buffer and initial state."""
        self._buffer = bytearray()
        self._state = ProtocolState.LOGIN

    def receive_data(self, data: bytes):
        """Append received data to buffer."""
        self._buffer.extend(data)

    def next_event(self) -> ProtocolEvent:
        """Process incoming data to protocol events."""
        if self._state == ProtocolState.LOGIN:
            if len(self._buffer) <= 2:
                return NeedMoreData()
            else:
                imei_len = int.from_bytes(self._buffer[0:2], "big")
                total_len = 2 + imei_len
                if len(self._buffer) < total_len:
                    return NeedMoreData()
                if len(self._buffer) == total_len:
                    raw_data = self._buffer[2:]
                    self._buffer = self._buffer[total_len:]
                    self._state = ProtocolState.DATA
                    return LoginPacket(data=raw_data)
                else:
                    return NeedMoreData()

        if self._state == ProtocolState.DATA:
            if len(self._buffer) < 8:
                return NeedMoreData()

            data_len = int.from_bytes(self._buffer[4:8], "big")
            total_len = 8 + data_len + 4

            if len(self._buffer) < total_len:
                return NeedMoreData()

            raw_packet = self._buffer[:total_len]
            data = raw_packet[8:-4]
            crc16 = int.from_bytes(raw_packet[-4:], "big")

            if Teltonika._crc16(data) != crc16:
                LOGGER.debug("CRC check failed.")
                return CRC16CheckFailed()

            self._buffer = self._buffer[total_len:]
            return AVLPacket(data=data)

        return NeedMoreData()

    @staticmethod
    def _crc16(data: bytes) -> int:
        """Calculate CRC-16-IBM."""
        crc = 0x0000
        for byte in data:
            crc ^= byte
            for _ in range(8):
                if crc & 1:
                    crc = (crc >> 1) ^ 0xA001
                else:
                    crc >>= 1
        return crc & 0xFFFF
