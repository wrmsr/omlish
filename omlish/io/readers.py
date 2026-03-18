# ruff: noqa: UP006 UP007 UP045
# @omlish-lite
"""
TODO:
 - s/bytes/BytesLike?
"""
import io
import typing as ta

from ..lite.namespaces import NamespaceClass


##


class RawBytesReader(ta.Protocol):
    """Maps to `io.BufferedIOBase`."""

    def read1(self, n: int = -1, /) -> bytes:
        """Return at most `n` bytes with at most a single underlying read."""


class BytesReader(RawBytesReader, ta.Protocol):
    def read(self, n: int = -1, /) -> bytes:
        """Return exactly `n` bytes unless EOF is reached.."""


class BytesReaders(NamespaceClass):
    @ta.final
    class Empty:
        def read1(self, n: int = -1, /) -> bytes:
            return b''

        def read(self, n: int = -1, /) -> bytes:
            return b''

    @ta.final
    class Static:
        def __init__(self, b: bytes) -> None:
            self._r = io.BytesIO(b)

        def read1(self, n: int = -1, /) -> bytes:
            return self._r.read1(n)

        def read(self, n: int = -1, /) -> bytes:
            return self._r.read(n)

    @classmethod
    def of_bytes(cls, b: bytes) -> BytesReader:
        if b:
            return cls.Static(b)
        else:
            return cls.Empty()


##


class AsyncRawBytesReader(ta.Protocol):
    def read1(self, n: int = -1, /) -> ta.Awaitable[bytes]:
        """Return at most `n` bytes with at most a single underlying read."""


class AsyncBytesReader(AsyncRawBytesReader, ta.Protocol):
    def read(self, n: int = -1, /) -> ta.Awaitable[bytes]:
        """Return exactly `n` bytes unless EOF is reached.."""


class AsyncBytesReaders(NamespaceClass):
    @ta.final
    class Empty:
        async def read1(self, n: int = -1, /) -> bytes:
            return b''

        async def read(self, n: int = -1, /) -> bytes:
            return b''

    @ta.final
    class Static:
        def __init__(self, b: bytes) -> None:
            self._r = io.BytesIO(b)

        async def read1(self, n: int = -1, /) -> bytes:
            return self._r.read1(n)

        async def read(self, n: int = -1, /) -> bytes:
            return self._r.read(n)

    @classmethod
    def of_bytes(cls, b: bytes) -> AsyncBytesReader:
        if b:
            return cls.Static(b)
        else:
            return cls.Empty()
