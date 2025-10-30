# ruff: noqa: UP045
# @omlish-lite
import typing as ta


##


class RawBytesReader(ta.Protocol):
    def read1(self, n: int = -1, /) -> bytes: ...


class BufferedBytesReader(RawBytesReader, ta.Protocol):
    def read(self, n: int = -1, /) -> bytes: ...

    def readall(self) -> bytes: ...


#


class AsyncRawBytesReader(ta.Protocol):
    def read1(self, n: int = -1, /) -> ta.Awaitable[bytes]: ...


class AsyncBufferedBytesReader(AsyncRawBytesReader, ta.Protocol):
    def read(self, n: int = -1, /) -> ta.Awaitable[bytes]: ...

    def readall(self) -> ta.Awaitable[bytes]: ...
