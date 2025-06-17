# ruff: noqa: UP006 UP007 UP045
# @omlish-lite
import typing as ta

from ..io.buffers import ReadableListBuffer


##


class AsyncBufferedReader:
    def __init__(
            self,
            read: ta.Callable[[], ta.Awaitable[bytes]],
    ) -> None:
        super().__init__()

        self._read = read

        self._buf = ReadableListBuffer()

    class Cancelled(Exception):  # noqa
        pass

    async def read_until(
            self,
            delim: bytes,
            *,
            canceller: ta.Optional[ta.Callable[[], bool]] = None,
    ) -> bytes:
        o = 0
        while True:
            if canceller is not None and canceller():
                raise self.Cancelled
            r = self._buf.read_until_(delim, o)
            if isinstance(r, bytes):
                return r
            o = r
            b = await self._read()
            if not b:
                raise EOFError
            self._buf.feed(b)

    async def read_exact(
            self,
            sz: int,
            *,
            canceller: ta.Optional[ta.Callable[[], bool]] = None,
    ) -> bytes:
        while True:
            if canceller is not None and canceller():
                raise self.Cancelled
            r = self._buf.read(sz)
            if r is not None:
                return r
            b = await self._read()
            if not b:
                raise EOFError
            self._buf.feed(b)
