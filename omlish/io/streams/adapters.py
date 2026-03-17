# ruff: noqa: UP006 UP007 UP045
# @omlish-lite
import abc
import io
import typing as ta

from ...lite.abstract import Abstract
from .direct import DirectByteStreamBufferView
from .errors import NeedMoreDataByteStreamBufferError
from .types import BytesLike
from .types import ByteStreamBuffer
from .types import ByteStreamBufferLike
from .types import ByteStreamBufferView
from .types import MutableByteStreamBuffer


BytesOrAwaitableBytes = ta.TypeVar('BytesOrAwaitableBytes', bound=ta.Union[bytes, ta.Awaitable[bytes]])
BytesOrAwaitableBytes_co = ta.TypeVar('BytesOrAwaitableBytes_co', bound=ta.Union[bytes, ta.Awaitable[bytes]], covariant=True)  # noqa

BoolOrAwaitableBool = ta.TypeVar('BoolOrAwaitableBool', bound=ta.Union[bool, ta.Awaitable[bool]])
BoolOrAwaitableBool_co = ta.TypeVar('BoolOrAwaitableBool_co', bound=ta.Union[bool, ta.Awaitable[bool]], covariant=True)


##


BaseByteStreamBufferBytesReaderAdapterPolicy = ta.Literal[  # ta.TypeAlias  # omlish-amalg-typing-no-move
    'raise',
    'return_partial',
    'fill',
]


class BaseByteStreamBufferBytesReaderAdapter(Abstract, ta.Generic[BytesOrAwaitableBytes, BoolOrAwaitableBool]):
    """
    Adapter: ByteStreamBuffer -> file-like buffered reader methods (`read1`, `read`).

    This adapter is policy-driven for how it behaves when insufficient bytes are available. The core buffer is
    intentionally non-blocking; blocking behavior (if desired) must be provided via a `fill` callback that supplies more
    bytes into the buffer.

    `policy`:
      - 'raise': raise `NeedMoreDataByteStreamBufferError` if fewer than `n` bytes are available (for `n >= 0`).
      - 'return_partial': return whatever is available (possibly b'') up to `n`.
      - 'fill': repeatedly call `fill()` until satisfied or until `fill()` signals EOF - effectively blocking mode.

    `fill`:
      - Callable that writes more bytes into the underlying buffer.

    This adapter exists for interop with legacy code that expects file-like objects, but the core design remains
    independent from `io` and blocking semantics.
    """

    DEFAULT_POLICY: ta.Final = 'raise'

    class Filler(ta.Protocol[BoolOrAwaitableBool_co]):
        def __call__(self, n: int, single: bool) -> BoolOrAwaitableBool_co:
            """
            Called when more data needs to be written into the underlying buffer.

            - If `n > 0` then at least `n` bytes are requested - extra bytes will be buffered.
            - If `single` then the user has requested that at most one underlying read operation should be performed.
            - If `n < 1` and `single` then any amount of data is requested.
            - If `n < 1` and not `single` then all remaining data is requested.

            Returns `True` if it made progress or more data may be available, or `False` if no more data will arrive.

            If not `single` returning `True` then at least 1 new byte mut have been written to the buffer (otherwise
            it would infinite loop).

            This function may or may not sleep / loop / block / etc. as it sees fit.
            """

    def __init__(
            self,
            buf: ByteStreamBuffer,
            *,
            policy: ta.Optional[BaseByteStreamBufferBytesReaderAdapterPolicy] = None,
            fill: ta.Optional[Filler[BoolOrAwaitableBool]] = None,
    ) -> None:
        super().__init__()

        self._buf = buf
        if fill is not None:
            if policy is None:
                policy = 'fill'
            elif policy != 'fill':
                raise ValueError('fill callback only valid with policy=fill')
        elif policy is None:
            policy = self.DEFAULT_POLICY
        self._policy = policy
        self._fill = fill

    #

    class RawBytesReader(ta.Protocol[BytesOrAwaitableBytes_co]):
        def read1(self, n: ta.Any) -> BytesOrAwaitableBytes_co: ...

    class BytesReader(RawBytesReader[BytesOrAwaitableBytes_co], ta.Protocol[BytesOrAwaitableBytes_co]):
        def read(self, n: ta.Any) -> BytesOrAwaitableBytes_co: ...

    @classmethod
    @abc.abstractmethod
    def wrap(
            cls,
            obj: RawBytesReader[BytesOrAwaitableBytes],
            buf: MutableByteStreamBuffer,
            *,
            policy: ta.Optional[BaseByteStreamBufferBytesReaderAdapterPolicy] = None,
    ) -> 'BaseByteStreamBufferBytesReaderAdapter[BytesOrAwaitableBytes, BoolOrAwaitableBool]':
        raise NotImplementedError

    #

    @abc.abstractmethod
    def read1(self, n: int = -1, /) -> BytesOrAwaitableBytes:
        raise NotImplementedError

    def _inner_read(self, n: int) -> ta.Union[bytes, ta.Literal['fill']]:
        buf = self._buf
        if (ln := len(buf)) >= n:
            return buf.split_to(n).tobytes()

        pol = self._policy
        if pol == 'return_partial':
            if not ln:
                return b''
            return buf.split_to(ln).tobytes()

        elif pol == 'raise':
            raise NeedMoreDataByteStreamBufferError

        elif pol == 'fill':
            return 'fill'

        else:
            raise RuntimeError(f'invalid policy: {pol!r}')

    @abc.abstractmethod
    def read(self, n: int = -1, /) -> BytesOrAwaitableBytes:
        raise NotImplementedError


#


class ByteStreamBufferBytesReaderAdapter(BaseByteStreamBufferBytesReaderAdapter[bytes, bool]):
    @classmethod
    def wrap(
            cls,
            obj: BaseByteStreamBufferBytesReaderAdapter.RawBytesReader[bytes],
            buf: MutableByteStreamBuffer,
            *,
            policy: ta.Optional[BaseByteStreamBufferBytesReaderAdapterPolicy] = None,
    ) -> 'BaseByteStreamBufferBytesReaderAdapter[bytes, bool]':
        if not hasattr(obj, 'read1'):
            raise TypeError(obj)

        elif hasattr(obj, 'read'):
            def br_fill(n: int, single: bool) -> bool:
                if single:
                    b = obj.read1(n)
                else:
                    b = obj.read(n)
                if not b:
                    return False
                buf.write(b)
                return True

            fill = br_fill

        else:
            def rbr_fill(n: int, single: bool) -> bool:
                b = obj.read1(n)
                if not b:
                    return False
                buf.write(b)
                return True

            fill = rbr_fill

        return cls(
            buf,
            policy=policy,
            fill=fill,
        )

    def read1(self, n: int = -1, /) -> bytes:
        if not n:
            return b''

        buf = self._buf
        if not (ln := len(buf)):
            if (fill := self._fill) is None:
                return b''

            fill(n, True)
            ln = len(buf)

        if not ln:
            return b''

        return buf.split_to(min(n, ln) if n > 0 else ln).tobytes()

    def read(self, n: int = -1, /) -> bytes:
        if n < 0:
            if (fill := self._fill) is not None:
                while fill(-1, False):
                    pass

            buf = self._buf
            return buf.split_to(len(buf)).tobytes()

        if not n:
            return b''

        buf = self._buf
        while True:
            if (out := self._inner_read(n)) != 'fill':
                return out

            ln = len(buf)
            if not self._fill(n - ln, False):  # type: ignore[misc]
                # EOF
                if not (ln := len(buf)):
                    return b''
                return buf.split_to(ln).tobytes()

            if len(buf) == ln:
                raise RuntimeError('fill did not produce data')


#


class ByteStreamBufferAsyncBytesReaderAdapter(BaseByteStreamBufferBytesReaderAdapter[ta.Awaitable[bytes], ta.Awaitable[bool]]):  # noqa
    @classmethod
    def wrap(
            cls,
            obj: BaseByteStreamBufferBytesReaderAdapter.RawBytesReader[ta.Awaitable[bytes]],
            buf: MutableByteStreamBuffer,
            *,
            policy: ta.Optional[BaseByteStreamBufferBytesReaderAdapterPolicy] = None,
    ) -> 'BaseByteStreamBufferBytesReaderAdapter[ta.Awaitable[bytes], ta.Awaitable[bool]]':
        if not hasattr(obj, 'read1'):
            raise TypeError(obj)

        elif hasattr(obj, 'read'):
            async def br_fill(n: int, single: bool) -> bool:
                if single:
                    b = await obj.read1(n)
                else:
                    b = await obj.read(n)
                if not b:
                    return False
                buf.write(b)
                return True

            fill = br_fill

        else:
            async def rbr_fill(n: int, single: bool) -> bool:
                b = await obj.read1(n)
                if not b:
                    return False
                buf.write(b)
                return True

            fill = rbr_fill

        return cls(
            buf,
            policy=policy,
            fill=fill,
        )

    async def read1(self, n: int = -1, /) -> bytes:
        if not n:
            return b''

        buf = self._buf
        if not (ln := len(buf)):
            if (fill := self._fill) is None:
                return b''

            await fill(n, True)
            ln = len(buf)

        if not ln:
            return b''

        return buf.split_to(min(n, ln) if n > 0 else ln).tobytes()

    async def read(self, n: int = -1, /) -> bytes:
        if n < 0:
            if (fill := self._fill) is not None:
                while await fill(-1, False):
                    pass

            buf = self._buf
            return buf.split_to(len(buf)).tobytes()

        if not n:
            return b''

        buf = self._buf
        while True:
            if (out := self._inner_read(n)) != 'fill':
                return out

            ln = len(buf)
            if not await self._fill(n - ln, False):  # type: ignore[misc]
                # EOF
                if not (ln := len(buf)):
                    return b''
                return buf.split_to(ln).tobytes()

            if len(buf) == ln:
                raise RuntimeError('fill did not produce data')


##


class ByteStreamBufferWriterAdapter:
    """
    Adapter: file-like writer sink <- ByteStreamBuffer / bytes-like.

    This is intentionally small and dumb: it exists to bridge into code expecting a `.write(...)` method on an object.

    If given a ByteStreamBufferView-like object, it writes segment-by-segment to avoid materializing copies when the
    sink can accept multiple writes efficiently.
    """

    def __init__(self, f: ta.Any) -> None:
        super().__init__()

        self._f = f

    def write(self, data: ta.Any) -> int:
        f = self._f

        if isinstance(data, (bytes, bytearray, memoryview)):
            b = data.tobytes() if isinstance(data, memoryview) else bytes(data)
            return ta.cast(int, f.write(b))

        if isinstance(data, ByteStreamBufferLike):
            total = 0
            for mv in data.segments():
                total += ta.cast(int, f.write(bytes(mv)))
            return total

        if isinstance(data, ByteStreamBufferView):
            b = data.tobytes()
            return ta.cast(int, f.write(b))

        raise TypeError(data)


##


class BytesIoByteStreamBuffer(MutableByteStreamBuffer):
    """
    ByteStreamBuffer/MutableByteStreamBuffer implementation backed by `io.BytesIO`, using `getbuffer()`.

    This exists primarily for interoperability with code that already produces/consumes `BytesIO`, and to demonstrate
    how `getbuffer()` can expose a non-copying `memoryview` of internal storage.

    Caveat (important):
      - Any exported `memoryview` from `BytesIO.getbuffer()` can pin the BytesIO against resizing.
      - If a caller holds onto a view and we attempt to grow/resize internally, `BytesIO` may raise `BufferError`.

    This backing is therefore best suited for controlled scenarios; it is *not* the recommended default buffer backend
    for applications (segmented/bytearray backends are more predictable).
    """

    def __init__(
            self,
            *,
            compaction_threshold: int = 64 * 1024,
    ) -> None:
        super().__init__()

        self._compaction_threshold = compaction_threshold

        self._bio = io.BytesIO()
        self._rpos = 0

        # reserve/commit state
        self._resv: ta.Optional[bytearray] = None
        self._resv_len = 0

    @property
    def max_size(self) -> ta.Optional[int]:
        return None

    def __len__(self) -> int:
        return self._bio.getbuffer().nbytes - self._rpos

    def peek(self) -> memoryview:
        mv = self._bio.getbuffer()
        return mv[self._rpos:]

    def segments(self) -> ta.Sequence[memoryview]:
        mv = self._bio.getbuffer()
        seg = mv[self._rpos:]
        return (seg,) if len(seg) else ()

    def advance(self, n: int, /) -> None:
        if n < 0 or n > len(self):
            raise ValueError(n)
        self._rpos += n
        # Optional compaction heuristic: if we've consumed a lot, rebuild a smaller BytesIO.
        # This may fail if someone holds a getbuffer() view (BufferError).
        if (
                self._rpos and
                self._rpos >= self._compaction_threshold and
                self._rpos >= (self._bio.getbuffer().nbytes // 2)
        ):
            try:
                remaining = self._bio.getbuffer()[self._rpos:].tobytes()
                self._bio = io.BytesIO(remaining)
                self._rpos = 0
            except BufferError as e:  # noqa
                raise

    def split_to(self, n: int, /) -> ByteStreamBufferView:
        if n < 0 or n > len(self):
            raise ValueError(n)
        mv = self._bio.getbuffer()
        out = mv[self._rpos:self._rpos + n]
        self._rpos += n
        return DirectByteStreamBufferView(out)

    def write(self, data: BytesLike, /) -> None:
        if not data:
            return
        if isinstance(data, memoryview):
            data = data.tobytes()
        try:
            self._bio.seek(0, io.SEEK_END)
            self._bio.write(data)
        except BufferError as e:  # noqa
            raise

    def reserve(self, n: int, /) -> memoryview:
        if n < 0:
            raise ValueError(n)
        if self._resv is not None:
            raise RuntimeError('outstanding reserve')
        b = bytearray(n)
        self._resv = b
        self._resv_len = n
        return memoryview(b)

    def commit(self, n: int, /) -> None:
        if self._resv is None:
            raise RuntimeError('no outstanding reserve')
        if n < 0 or n > self._resv_len:
            raise ValueError(n)
        b = self._resv
        self._resv = None
        self._resv_len = 0
        if n:
            self.write(memoryview(b)[:n])

    def coalesce(self, n: int, /) -> memoryview:
        if n < 0 or n > len(self):
            raise ValueError(n)
        if not n:
            return memoryview(b'')
        # BytesIO is always contiguous, just return the requested slice
        mv = self._bio.getbuffer()
        return mv[self._rpos:self._rpos + n]

    def find(self, sub: bytes, start: int = 0, end: ta.Optional[int] = None) -> int:
        # Normalize start/end to valid range
        s, e, _ = slice(start, end, 1).indices(len(self))
        if e < s:
            e = s

        if not sub:
            return s

        # Convert to bytes for searching (memoryview doesn't have find method)
        b = bytes(self._bio.getbuffer())
        idx = b.find(sub, self._rpos + s, self._rpos + e)
        return (idx - self._rpos) if idx >= 0 else -1

    def rfind(self, sub: bytes, start: int = 0, end: ta.Optional[int] = None) -> int:
        # Normalize start/end to valid range
        s, e, _ = slice(start, end, 1).indices(len(self))
        if e < s:
            e = s

        if not sub:
            return e

        # Convert to bytes for searching (memoryview doesn't have rfind method)
        b = bytes(self._bio.getbuffer())
        idx = b.rfind(sub, self._rpos + s, self._rpos + e)
        return (idx - self._rpos) if idx >= 0 else -1
