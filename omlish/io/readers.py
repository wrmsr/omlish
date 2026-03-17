# ruff: noqa: UP006 UP007 UP045
# @omlish-lite
import typing as ta


##


class RawBytesReader(ta.Protocol):
    """Maps to `io.BufferedIOBase`."""

    def read1(self, n: int = -1, /) -> bytes:
        """Return at most `n` bytes with at most a single underlying read."""


class BytesReader(RawBytesReader, ta.Protocol):
    def read(self, n: int = -1, /) -> bytes:
        """Return exactly `n` bytes unless EOF is reached.."""


#


class AsyncRawBytesReader(ta.Protocol):
    def read1(self, n: int = -1, /) -> ta.Awaitable[bytes]:
        """Return at most `n` bytes with at most a single underlying read."""


class AsyncBytesReader(AsyncRawBytesReader, ta.Protocol):
    def read(self, n: int = -1, /) -> ta.Awaitable[bytes]:
        """Return exactly `n` bytes unless EOF is reached.."""
