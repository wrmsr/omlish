# ruff: noqa: UP006 UP007 UP043 UP045
# @omlish-lite
"""
TODO:
 - overhaul and just coro-ify pyio?
"""
import io
import typing as ta

from ..lite.attrops import attr_repr
from ..lite.check import check
from .readers import AsyncBufferedBytesReader
from .readers import AsyncRawBytesReader
from .readers import BufferedBytesReader
from .readers import RawBytesReader


##


class DelimitingBuffer:
    """
    https://github.com/python-trio/trio/issues/796 :|

    FIXME: when given overlapping delimiters like [b'\r', b'\r\n'], *should* refuse to output a line ending in '\r'
      without knowing it will not be followed by '\n'. does not currently do this - currently only picks longest
      delimiter present in the buffer. does this need a prefix-trie? is this borderline parsing?
    """

    #

    class Error(Exception):
        def __init__(self, buffer: 'DelimitingBuffer') -> None:
            super().__init__(buffer)

            self.buffer = buffer

        def __repr__(self) -> str:
            return attr_repr(self, 'buffer')

    class ClosedError(Error):
        pass

    #

    DEFAULT_DELIMITERS: bytes = b'\n'

    def __init__(
            self,
            delimiters: ta.Iterable[ta.Union[int, bytes]] = DEFAULT_DELIMITERS,
            *,
            keep_ends: bool = False,
            max_size: ta.Optional[int] = None,
    ) -> None:
        super().__init__()

        ds: ta.Set[bytes] = set()
        for d in delimiters:
            if isinstance(d, int):
                d = bytes([d])
            ds.add(check.isinstance(d, bytes))

        self._delimiters: ta.FrozenSet[bytes] = frozenset(ds)
        self._keep_ends = keep_ends
        self._max_size = max_size

        self._buf: ta.Optional[io.BytesIO] = io.BytesIO()

        ddl = {}
        dl = sorted(self._delimiters, key=lambda d: -len(d))
        for i, d in enumerate(dl):
            for j, d2 in enumerate(dl):
                if len(d2) < len(d):
                    break
                if i == j or not d2.startswith(d):
                    continue
                ddl[d] = len(d2)
                break
        self._delimiter_disambiguation_lens: ta.Dict[bytes, int] = ddl

    #

    @property
    def is_closed(self) -> bool:
        return self._buf is None

    def tell(self) -> int:
        if (buf := self._buf) is None:
            raise self.ClosedError(self)
        return buf.tell()

    def peek(self) -> bytes:
        if (buf := self._buf) is None:
            raise self.ClosedError(self)
        return buf.getvalue()

    def _find_delim(self, data: ta.Union[bytes, bytearray], i: int) -> ta.Optional[ta.Tuple[int, int]]:
        rp = None  # type: int | None
        rl = None  # type: int | None
        rd = None  # type: bytes | None

        for d in self._delimiters:
            if (p := data.find(d, i)) < 0:
                continue

            dl = len(d)

            if rp is None or p < rp:
                rp, rl, rd = p, dl, d
            elif rp == p and rl < dl:  # type: ignore
                rl, rd = dl, d  # noqa

        if rp is None:
            return None

        # FIXME:
        # if (ddl := self._delimiter_disambiguation_lens.get(rd)) is not None:
        #     raise NotImplementedError

        return rp, rl  # type: ignore

    def _append_and_reset(self, chunk: bytes) -> bytes:
        buf = check.not_none(self._buf)
        if not buf.tell():
            return chunk

        buf.write(chunk)
        ret = buf.getvalue()
        buf.seek(0)
        buf.truncate()
        return ret

    class Incomplete(ta.NamedTuple):
        b: bytes

    def feed(self, data: ta.Union[bytes, bytearray]) -> ta.Generator[ta.Union[bytes, Incomplete], None, None]:
        if (buf := self._buf) is None:
            raise self.ClosedError(self)

        if not data:
            self._buf = None

            if buf.tell():
                yield self.Incomplete(buf.getvalue())

            return

        l = len(data)
        i = 0
        while i < l:
            if (pt := self._find_delim(data, i)) is None:
                break

            p, pl = pt
            n = p + pl
            if self._keep_ends:
                p = n

            yield self._append_and_reset(data[i:p])

            i = n

        if i >= l:
            return

        if self._max_size is None:
            buf.write(data[i:])
            return

        while i < l:
            remaining_data_len = l - i
            remaining_buf_capacity = self._max_size - buf.tell()

            if remaining_data_len < remaining_buf_capacity:
                buf.write(data[i:])
                return

            p = i + remaining_buf_capacity
            yield self.Incomplete(self._append_and_reset(data[i:p]))
            i = p


##


class ReadableListBuffer:
    # FIXME: merge with PrependableGeneratorReader

    def __init__(self) -> None:
        super().__init__()

        self._lst: list[bytes] = []

    def __bool__(self) -> ta.NoReturn:
        raise TypeError("Use 'buf is not None' or 'len(buf)'.")

    def __len__(self) -> int:
        return sum(map(len, self._lst))

    def feed(self, d: bytes) -> None:
        if d:
            self._lst.append(d)

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

        return o

    def read(self, n: ta.Optional[int] = None) -> ta.Optional[bytes]:
        if n is None:
            if not self._lst:
                return b''

            o = b''.join(self._lst)
            self._lst = []
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
            return self._buf.read(n) or b''

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
            return self._buf.read(n) or b''

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
            n = fn(check.not_empty(d))
            if not n:
                break
            t += n

        if t:
            self._lst = [
                *([d[n:]] if n < len(d) else []),
                *lst[i + 1:],
            ]
            self._pos += t

        return t
