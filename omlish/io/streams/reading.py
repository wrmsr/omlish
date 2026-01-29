# @omlish-lite
from .errors import NeedMoreDataByteStreamBufferError
from .types import ByteStreamBuffer
from .types import ByteStreamBufferView


##


class ByteStreamBufferReader:
    def __init__(self, buf: ByteStreamBuffer) -> None:
        super().__init__()

        self._buf = buf

    #

    def _coalesce_exact(self, n: int) -> memoryview:
        """
        Return a contiguous view of exactly `n` readable bytes, or raise NeedMoreDataByteStreamBufferError.

        Uses `buf.coalesce(n)` to avoid per-byte Python work and to keep copying close to the buffer backend.
        """

        if n < 0:
            raise ValueError(n)
        if len(self._buf) < n:
            raise NeedMoreDataByteStreamBufferError
        mv = self._buf.coalesce(n)
        if len(mv) < n:
            # Defensive: coalesce contract should provide >= n when len(buf) >= n.
            raise NeedMoreDataByteStreamBufferError
        return mv[:n]

    #

    def peek_u8(self) -> int:
        """Peek an unsigned 8-bit integer without consuming."""

        mv = self._coalesce_exact(1)
        return mv[0]

    def read_u8(self) -> int:
        """Read and consume an unsigned 8-bit integer."""

        v = self.peek_u8()
        self._buf.advance(1)
        return v

    def peek_u16_be(self) -> int:
        """Peek an unsigned 16-bit big-endian integer without consuming."""

        mv = self._coalesce_exact(2)
        return int.from_bytes(mv, 'big', signed=False)

    def read_u16_be(self) -> int:
        """Read and consume an unsigned 16-bit big-endian integer."""

        v = self.peek_u16_be()
        self._buf.advance(2)
        return v

    def peek_u16_le(self) -> int:
        """Peek an unsigned 16-bit little-endian integer without consuming."""

        mv = self._coalesce_exact(2)
        return int.from_bytes(mv, 'little', signed=False)

    def read_u16_le(self) -> int:
        """Read and consume an unsigned 16-bit little-endian integer."""

        v = self.peek_u16_le()
        self._buf.advance(2)
        return v

    def peek_u32_be(self) -> int:
        """Peek an unsigned 32-bit big-endian integer without consuming."""

        mv = self._coalesce_exact(4)
        return int.from_bytes(mv, 'big', signed=False)

    def read_u32_be(self) -> int:
        """Read and consume an unsigned 32-bit big-endian integer."""

        v = self.peek_u32_be()
        self._buf.advance(4)
        return v

    def peek_u32_le(self) -> int:
        """Peek an unsigned 32-bit little-endian integer without consuming."""

        mv = self._coalesce_exact(4)
        return int.from_bytes(mv, 'little', signed=False)

    def read_u32_le(self) -> int:
        """Read and consume an unsigned 32-bit little-endian integer."""

        v = self.peek_u32_le()
        self._buf.advance(4)
        return v

    #

    def peek_exact(self, n: int, /) -> memoryview:
        """
        Return a contiguous view of exactly `n` readable bytes without consuming.

        Raises NeedMoreDataByteStreamBufferError if fewer than `n` bytes are currently buffered.
        """

        if n < 0:
            raise ValueError(n)
        if len(self._buf) < n:
            raise NeedMoreDataByteStreamBufferError
        mv = self._buf.coalesce(n)
        if len(mv) < n:
            raise NeedMoreDataByteStreamBufferError
        return mv[:n]

    def take(self, n: int, /) -> ByteStreamBufferView:
        """
        Consume and return a `ByteStreamBufferView`-like object representing exactly `n` bytes.

        Raises NeedMoreDataByteStreamBufferError if fewer than `n` bytes are currently buffered.
        """

        if n < 0:
            raise ValueError(n)
        if len(self._buf) < n:
            raise NeedMoreDataByteStreamBufferError
        return self._buf.split_to(n)

    def read_bytes(self, n: int, /) -> bytes:
        """
        Consume exactly `n` bytes and return them as a contiguous `bytes` object (copy boundary).

        Raises NeedMoreDataByteStreamBufferError if fewer than `n` bytes are currently buffered.
        """

        v = self.take(n)
        return v.tobytes()
