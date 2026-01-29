# ruff: noqa: UP006 UP007 UP045
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


##


class FileLikeRawBytesReader:
    """
    Adapter: file-like object -> RawBytesReader-style `read1`.

    This is intentionally permissive: it duck-types common file-like APIs.

    Notes:
      - If the object has `read1`, we use it.
      - Otherwise we fall back to `read`.
      - This is a *raw* reader: it makes no buffering guarantees beyond what the wrapped object provides.
    """

    def __init__(self, f: ta.Any) -> None:
        super().__init__()

        self._f = f

    def read1(self, n: int = -1, /) -> bytes:
        f = self._f
        if hasattr(f, 'read1'):
            return ta.cast(bytes, f.read1(n))
        return ta.cast(bytes, f.read(n))


class FileLikeBufferedBytesReader(FileLikeRawBytesReader):
    """
    Adapter: file-like object -> BufferedBytesReader-style `read/readall`.

    Notes:
      - Uses `readall` if present; otherwise uses `read()` with `-1`.
      - Does not impose additional buffering; it reflects the wrapped object's behavior.
    """

    def read(self, n: int = -1, /) -> bytes:
        return ta.cast(bytes, self._f.read(n))

    def readall(self) -> bytes:
        f = self._f
        if hasattr(f, 'readall'):
            return ta.cast(bytes, f.readall())
        return ta.cast(bytes, f.read())
