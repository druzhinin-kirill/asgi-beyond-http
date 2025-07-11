"""Script to emulate vehicle session."""

import struct
import datetime
import socket
import time
import csv

from teltonika import AcceptPacket


def create_imei_packet(imei: str) -> bytes:
    imei_bytes = imei.encode("ascii")
    imei_length = len(imei_bytes)
    packet = struct.pack(">H", imei_length) + imei_bytes
    return packet


def encode_codec8_avl_record(
    timestamp=None,
    priority=0,
    lon=0.0,
    lat=0.0,
    altitude=0,
    angle=0,
    satellites=5,
    speed=0,
    event_id=0,
    io_elements=None,
):
    # Default timestamp: current UTC time
    if timestamp is None:
        timestamp = int(datetime.datetime.now().timestamp() * 1000)

    # Convert lat/lon to integer representation
    lat = int(lat * 10_000_000)
    lon = int(lon * 10_000_000)

    # Start building the binary record
    record = b""

    # Timestamp: 8 bytes
    record += struct.pack(">Q", timestamp)

    # Priority: 1 byte
    record += struct.pack("B", priority)

    # GPS Element: 15 bytes
    record += struct.pack(">i", lon)
    record += struct.pack(">i", lat)
    record += struct.pack(">H", altitude)
    record += struct.pack(">H", angle)
    record += struct.pack("B", satellites)
    record += struct.pack(">H", speed)

    # IO Element section
    if io_elements is None:
        io_elements = {}

    # Event ID (1 byte) and total IO count (1 byte)
    record += struct.pack("B", event_id)
    record += struct.pack("B", len(io_elements))

    # IO Elements (1 byte, 2 byte, 4 byte, 8 byte)
    for size in (1, 2, 4, 8):
        filtered = {
            k: v
            for k, v in io_elements.items()
            if isinstance(v, int) and v.bit_length() <= size * 8
        }
        record += struct.pack("B", len(filtered))
        for io_id, value in filtered.items():
            fmt = {1: "B", 2: ">H", 4: ">I", 8: ">Q"}[size]
            record += struct.pack("B", io_id)
            record += struct.pack(fmt, value)

    return record


def create_codec8_message(
    timestamp=None,
    lat=54.6872,
    lon=25.2797,
    altitude=100,
    angle=0,
    satellites=5,
    speed=10,
    priority=0,
    event_id=0,
    io_elements=None,
):
    codec_id = 0x08
    avl_count = 1

    # Encode one AVL record
    avl_record = encode_codec8_avl_record(
        timestamp=timestamp,
        lat=lat,
        lon=lon,
        altitude=altitude,
        angle=angle,
        satellites=satellites,
        speed=speed,
        priority=priority,
        event_id=event_id,
        io_elements=io_elements,
    )

    # Build data field
    data = struct.pack("B", codec_id)
    data += struct.pack("B", avl_count)
    data += avl_record
    data += struct.pack("B", avl_count)  # number of records again

    data_length = struct.pack(">I", len(data))

    # Calculate CRC16
    crc = struct.pack(">I", crc16(data))

    # Prepend data length (4 bytes) and append CRC (4 bytes)
    tcp_message = b"\x00\x00\x00\x00"  # placeholder for 4 bytes AVL length

    tcp_message = tcp_message + data_length + data + crc

    return tcp_message


def crc16(data: bytes) -> int:
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


def vehicle_session(address: tuple[str, int], filename: str, imei: str, sleep: float):
    """Send telemetry data"""
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(address)

    # Send IMEI packet first
    imei_packet = create_imei_packet(imei)
    client_socket.send(imei_packet)

    # Verify auth
    auth_response = client_socket.recv(1)
    if auth_response != AcceptPacket.code:
        raise RuntimeError("Failed to authenticate to server.")

    with open(filename, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            msg = create_codec8_message(
                lat=float(row["Latitude"]),
                lon=float(row["Longitude"]),
                speed=int(row["Speed"]),
                timestamp=int(datetime.datetime.now().timestamp()),
            )
            client_socket.send(msg)
            avl_response = int.from_bytes(client_socket.recv(4))

            # Very data acknowledged.
            if avl_response != 1:
                raise RuntimeError("Vehicle data was not acknowledged.")
            time.sleep(sleep)


if __name__ == "__main__":
    filename = "python.csv"
    address = ("localhost", 8081)
    imei = "123456789012345"
    vehicle_session(address, filename, imei, 0.01)
