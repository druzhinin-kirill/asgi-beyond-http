import struct
import datetime
import socket
import time


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


def vehicle_session(msgs: list[bytes], sleep: int) -> bytes:
    clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientsocket.connect(("localhost", 8081))

    for msg in msgs:
        clientsocket.send(msg)
        time.sleep(sleep)


# Example usage:
if __name__ == "__main__":
    msgs = [
        create_codec8_message(lat=52.5200, lon=13.4050, speed=50),
        create_codec8_message(lat=52.5195, lon=13.4045, speed=50),
        create_codec8_message(lat=52.5190, lon=13.4040, speed=50),
        create_codec8_message(lat=52.5185, lon=13.4037, speed=50),
        create_codec8_message(lat=52.5180, lon=13.4035, speed=50),
        create_codec8_message(lat=52.5175, lon=13.4038, speed=50),
        create_codec8_message(lat=52.5172, lon=13.4042, speed=50),
        create_codec8_message(lat=52.5170, lon=13.4048, speed=50),
        create_codec8_message(lat=52.5170, lon=13.4055, speed=50),
        create_codec8_message(lat=52.5173, lon=13.4062, speed=50),
        create_codec8_message(lat=52.5178, lon=13.4068, speed=50),
        create_codec8_message(lat=52.5182, lon=13.4073, speed=50),
        create_codec8_message(lat=52.5186, lon=13.4077, speed=50),
        create_codec8_message(lat=52.5190, lon=13.4080, speed=50),
        create_codec8_message(lat=52.5195, lon=13.4082, speed=50),
        create_codec8_message(lat=52.5200, lon=13.4083, speed=50),
        create_codec8_message(lat=52.5205, lon=13.4082, speed=50),
        create_codec8_message(lat=52.5210, lon=13.4080, speed=50),
        create_codec8_message(lat=52.5214, lon=13.4077, speed=50),
        create_codec8_message(lat=52.5218, lon=13.4073, speed=50),
        create_codec8_message(lat=52.5222, lon=13.4068, speed=50),
        create_codec8_message(lat=52.5227, lon=13.4062, speed=50),
        create_codec8_message(lat=52.5230, lon=13.4055, speed=50),
        create_codec8_message(lat=52.5230, lon=13.4048, speed=50),
        create_codec8_message(lat=52.5228, lon=13.4042, speed=50),
        create_codec8_message(lat=52.5225, lon=13.4038, speed=50),
        create_codec8_message(lat=52.5220, lon=13.4035, speed=50),
        create_codec8_message(lat=52.5215, lon=13.4037, speed=50),
        create_codec8_message(lat=52.5210, lon=13.4040, speed=50),
        create_codec8_message(lat=52.5205, lon=13.4045, speed=50),
        create_codec8_message(lat=52.5200, lon=13.4050, speed=50),
    ]
    vehicle_session(msgs, 1)
    # print("Codec8 TCP Message (hex):", msg.hex())
