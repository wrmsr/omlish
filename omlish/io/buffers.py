# ruff: noqa: UP006 UP007 UP043 UP045
# @omlish-lite
"""
TODO:
 - overhaul and just coro-ify pyio?
"""
import io
import typing as ta

from ..lite.check import check
from .readers import AsyncBufferedBytesReader
from .readers import AsyncRawBytesReader
from .readers import BufferedBytesReader
from .readers import RawBytesReader


##


class ReadableListBuffer:
    # FIXME: merge with PrependableGeneratorReader
    # FIXME: AND PUSHBACKREADER
    # FIXME: replace this whole thing with ByteStreamBuffers

    def __init__(self) -> None:
        super().__init__()

        self._lst: list[bytes] = []
        self._len = 0

    def __bool__(self) -> ta.NoReturn:
        raise TypeError("Use 'buf is not None' or 'len(buf)'.")

    def __len__(self) -> int:
        return self._len

    def feed(self, d: bytes) -> None:
        if d:
            self._lst.append(d)
            self._len += len(d)

    def _chop(self, i: int, e: int) -> bytes:
        lst = self._lst
        d = lst[i]

        o = b''.join([
            *lst[:i],
            d[:e],
        ])

        self._lst = [
            *([d[e:]] if e < len(d) else []),
            *lst[i + 1:],
        ]

        self._len -= len(o)

        return o

    def read(self, n: ta.Optional[int] = None) -> ta.Optional[bytes]:
        if n is None:
            if not self._lst:
                return b''

            o = b''.join(self._lst)
            self._lst = []
            self._len = 0
            return o

        if not (lst := self._lst):
            return None

        c = 0
        for i, d in enumerate(lst):
            r = n - c
            if (l := len(d)) >= r:
                return self._chop(i, r)
            c += l

        return None

    def read_exact(self, sz: int) -> bytes:
        d = self.read(sz)
        if d is None or len(d) != sz:
            raise EOFError(f'ReadableListBuffer got {"no" if d is None else len(d)}, expected {sz}')
        return d

    def read_until_(self, delim: bytes = b'\n', start_buffer: int = 0) -> ta.Union[bytes, int]:
        if not (lst := self._lst):
            return 0

        i = start_buffer
        while i < len(lst):
            if (p := lst[i].find(delim)) >= 0:
                return self._chop(i, p + len(delim))
            i += 1

        return i

    def read_until(self, delim: bytes = b'\n') -> ta.Optional[bytes]:
        r = self.read_until_(delim)
        return r if isinstance(r, bytes) else None

    #

    DEFAULT_BUFFERED_READER_CHUNK_SIZE: ta.ClassVar[int] = -1

    @ta.final
    class _BufferedBytesReader(BufferedBytesReader):
        def __init__(
                self,
                raw: RawBytesReader,
                buf: 'ReadableListBuffer',
                *,
                chunk_size: ta.Optional[int] = None,
        ) -> None:
            self._raw = raw
            self._buf = buf
            self._chunk_size = chunk_size or ReadableListBuffer.DEFAULT_BUFFERED_READER_CHUNK_SIZE

        def read1(self, n: int = -1, /) -> bytes:
            if n < 0:
                n = self._chunk_size
            if not n:
                return b''
            if 0 < n <= len(self._buf):
                return self._buf.read(n) or b''
            return self._raw.read1(n)

        def read(self, /, n: int = -1) -> bytes:
            if n < 0:
                return self.readall()
            while len(self._buf) < n:
                if not (b := self._raw.read1(n)):
                    break
                self._buf.feed(b)

            if len(self._buf) >= n:
                return self._buf.read(n) or b''

            # EOF with a partial buffer: return what we have.
            return self._buf.read() or b''

        def readall(self) -> bytes:
            buf = io.BytesIO()
            buf.write(self._buf.read() or b'')
            while (b := self._raw.read1(self._chunk_size)):
                buf.write(b)
            return buf.getvalue()

    def new_buffered_reader(
            self,
            raw: RawBytesReader,
            *,
            chunk_size: ta.Optional[int] = None,
    ) -> BufferedBytesReader:
        return self._BufferedBytesReader(
            raw,
            self,
            chunk_size=chunk_size,
        )

    @ta.final
    class _AsyncBufferedBytesReader(AsyncBufferedBytesReader):
        def __init__(
                self,
                raw: AsyncRawBytesReader,
                buf: 'ReadableListBuffer',
                *,
                chunk_size: ta.Optional[int] = None,
        ) -> None:
            self._raw = raw
            self._buf = buf
            self._chunk_size = chunk_size or ReadableListBuffer.DEFAULT_BUFFERED_READER_CHUNK_SIZE

        async def read1(self, n: int = -1, /) -> bytes:
            if n < 0:
                n = self._chunk_size
            if not n:
                return b''
            if 0 < n <= len(self._buf):
                return self._buf.read(n) or b''
            return await self._raw.read1(n)

        async def read(self, /, n: int = -1) -> bytes:
            if n < 0:
                return await self.readall()
            while len(self._buf) < n:
                if not (b := await self._raw.read1(n)):
                    break
                self._buf.feed(b)

            if len(self._buf) >= n:
                return self._buf.read(n) or b''

            # EOF with a partial buffer: return what we have.
            return self._buf.read() or b''

        async def readall(self) -> bytes:
            buf = io.BytesIO()
            buf.write(self._buf.read() or b'')
            while b := await self._raw.read1(self._chunk_size):
                buf.write(b)
            return buf.getvalue()

    def new_async_buffered_reader(
            self,
            raw: AsyncRawBytesReader,
            *,
            chunk_size: ta.Optional[int] = None,
    ) -> AsyncBufferedBytesReader:
        return self._AsyncBufferedBytesReader(
            raw,
            self,
            chunk_size=chunk_size,
        )


##


class IncrementalWriteBuffer:
    def __init__(
            self,
            data: bytes,
            *,
            write_size: int = 0x10000,
    ) -> None:
        super().__init__()

        check.not_empty(data)
        self._len = len(data)
        self._write_size = write_size

        self._lst = [
            data[i:i + write_size]
            for i in range(0, len(data), write_size)
        ]
        self._pos = 0

    @property
    def rem(self) -> int:
        return self._len - self._pos

    def write(self, fn: ta.Callable[[bytes], int]) -> int:
        lst = check.not_empty(self._lst)

        t = 0
        for i, d in enumerate(lst):  # noqa
            d = check.not_empty(d)
            n = fn(d)
            if not n:
                break

            if n > len(d):
                raise ValueError(n)

            t += n

            if n < len(d):
                # Short write - keep the remainder of this chunk and stop.
                self._lst = [
                    d[n:],
                    *lst[i + 1:],
                ]
                self._pos += t
                return t

        if t:
            # Only fully-written chunks were consumed.
            self._lst = lst[i + 1:]
            self._pos += t

        return t
