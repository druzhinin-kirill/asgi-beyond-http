"""ByteReader implementation."""

import io
import struct


class ByteReader:
    """Util to process protocol bytes."""

    def __init__(self, data: bytes):
        self.stream = io.BytesIO(data)

    def read(self, n: int) -> bytes:
        """Read n bytes."""
        return self.stream.read(n)

    def read_u8(self) -> int:
        """Read u8."""
        return struct.unpack(">B", self.read(1))[0]

    def read_u16(self) -> int:
        """Read u16."""
        return struct.unpack(">H", self.read(2))[0]

    def read_u32(self) -> int:
        """Read u32."""
        return struct.unpack(">I", self.read(4))[0]

    def read_u64(self) -> int:
        """Read u64."""
        return struct.unpack(">Q", self.read(8))[0]

    def read_i16(self) -> int:
        """Read i16."""
        return struct.unpack(">h", self.read(2))[0]

    def read_i32(self) -> int:
        """Read i32."""
        return struct.unpack(">i", self.read(4))[0]

    def tell(self) -> int:
        """Get current stream position."""
        return self.stream.tell()

    def seek(self, pos: int):
        """Change the stream position to the given byte offset."""
        self.stream.seek(pos)
