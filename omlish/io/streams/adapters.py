# ruff: noqa: UP006 UP007 UP045
# @omlish-lite
import io
import typing as ta

from .direct import DirectByteStreamBufferView
from .errors import NeedMoreDataByteStreamBufferError
from .types import BytesLike
from .types import ByteStreamBuffer
from .types import ByteStreamBufferLike
from .types import ByteStreamBufferView
from .types import MutableByteStreamBuffer


##


class ByteStreamBufferReaderAdapter:
    """
    Adapter: ByteStreamBuffer -> file-like reader methods (`read1`, `read`, `readall`).

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

    class Filler(ta.Protocol):
        def __call__(self, n: int, single: bool) -> bool:
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
            policy: ta.Literal['raise', 'return_partial', 'fill', None] = None,
            fill: ta.Optional[Filler] = None,
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
            return self.readall()

        if not n:
            return b''

        buf = self._buf
        pol = self._policy
        while True:
            if (ln := len(buf)) >= n:
                return buf.split_to(n).tobytes()

            if pol == 'return_partial':
                if not ln:
                    return b''
                return buf.split_to(ln).tobytes()

            elif pol == 'raise':
                raise NeedMoreDataByteStreamBufferError

            elif pol == 'fill':
                if not self._fill(n - ln, False):  # type: ignore[misc]
                    # EOF
                    if not ln:
                        return b''
                    return buf.split_to(ln).tobytes()

                if len(buf) == ln:
                    raise RuntimeError('fill did not produce data')

            else:
                raise RuntimeError(f'invalid policy: {pol!r}')

    def readall(self) -> bytes:
        if (fill := self._fill) is not None:
            fill(-1, False)

        buf = self._buf
        return buf.split_to(len(buf)).tobytes()


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
