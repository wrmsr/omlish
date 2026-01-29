# ruff: noqa: UP006 UP007 UP045
# @omlish-lite
import io
import time
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
      - 'raise': raise NeedMoreDataByteStreamBufferError if fewer than `n` bytes are available (for n >= 0).
      - 'return_partial': return whatever is available (possibly b'') up to `n`.
      - 'block': repeatedly call `fill()` until satisfied or until `fill()` signals EOF.

    `fill`:
      - Callable that writes more bytes into the underlying MutableByteStreamBuffer and returns:
          * True  -> made progress / more data may be available
          * False -> EOF / no more data will arrive
      - Only used when policy == 'block'.

    This adapter exists for interop with legacy code that expects file-like objects, but the core design remains
    independent from `io` and blocking semantics.
    """

    def __init__(
            self,
            buf: ByteStreamBuffer,
            *,
            policy: ta.Literal['raise', 'return_partial', 'block'] = 'raise',
            fill: ta.Optional[ta.Callable[[], bool]] = None,
            block_sleep: ta.Union[ta.Callable[[], None], float, None] = None,
    ) -> None:
        super().__init__()

        self._buf = buf
        self._policy = policy
        self._fill = fill
        self._block_sleep = block_sleep

        if self._policy == 'block' and self._fill is None:
            raise ValueError('policy=block requires fill')

    def _on_block(self) -> None:
        if (bs := self._block_sleep) is None:
            return
        elif callable(bs):
            bs()
        else:
            time.sleep(bs)

    def read1(self, n: int = -1, /) -> bytes:
        return self.read(n)

    def read(self, n: int = -1, /) -> bytes:
        buf = self._buf

        if n is None or n < 0:
            return self.readall()

        if not n:
            return b''

        while True:
            ln = len(buf)
            if ln >= n:
                v = buf.split_to(n)
                return v.tobytes()

            if self._policy == 'return_partial':
                if not ln:
                    return b''
                v = buf.split_to(ln)
                return v.tobytes()

            if self._policy == 'raise':
                raise NeedMoreDataByteStreamBufferError

            # block
            if not ta.cast('ta.Callable[[], bool]', self._fill)():
                # EOF
                if not ln:
                    return b''
                v = buf.split_to(ln)
                return v.tobytes()

            self._on_block()

    def readall(self) -> bytes:
        buf = self._buf
        parts: ta.List[bytes] = []

        while True:
            ln = len(buf)
            if ln:
                v = buf.split_to(ln)
                parts.append(v.tobytes())
                continue

            if self._policy == 'block':
                if not ta.cast('ta.Callable[[], bool]', self._fill)():
                    break
                self._on_block()
                continue

            break

        return b''.join(parts)


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
            compaction_threshold: int = 1 << 16,
    ) -> None:
        super().__init__()

        self._compaction_threshold = compaction_threshold

        self._bio = io.BytesIO()
        self._rpos = 0

        # reserve/commit state
        self._resv: ta.Optional[bytearray] = None
        self._resv_len = 0

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
