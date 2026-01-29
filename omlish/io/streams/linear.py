# ruff: noqa: UP006 UP007 UP045
# @omlish-lite
import typing as ta

from .base import BaseByteStreamBufferLike
from .errors import BufferTooLargeByteStreamBufferError
from .errors import NoOutstandingReserveByteStreamBufferError
from .errors import OutstandingReserveByteStreamBufferError
from .segmented import SegmentedByteStreamBufferView
from .types import BytesLike
from .types import MutableByteStreamBuffer


##


class LinearByteStreamBuffer(BaseByteStreamBufferLike, MutableByteStreamBuffer):
    """
    A simple contiguous (bytearray-backed) MutableByteStreamBuffer implementation.

    Strengths:
      - Fast `find/rfind` and contiguous peeking.
      - Efficient reserve/commit into a single backing store.

    Tradeoffs:
      - `split_to` returns a stable view by copying the split bytes into an owned `bytes` object.
        (A truly zero-copy split view would require pinning the underlying bytearray against compaction.)
    """

    def __init__(
            self,
            *,
            max_bytes: ta.Optional[int] = None,
            initial_capacity: int = 0,
    ) -> None:
        super().__init__()

        self._max_bytes = None if max_bytes is None else int(max_bytes)

        if initial_capacity < 0:
            raise ValueError(initial_capacity)
        if self._max_bytes is not None and initial_capacity > self._max_bytes:
            raise BufferTooLargeByteStreamBufferError('buffer exceeded max_bytes')

        # Pre-size the backing store to encourage fewer resizes/copies on trickle-y writes.
        # We immediately clear so readable length remains 0.
        if initial_capacity:
            self._ba = bytearray(initial_capacity)
            self._ba.clear()
        else:
            self._ba = bytearray()

    _rpos = 0
    _wpos = 0

    _resv_start: ta.Optional[int] = None
    _resv_len = 0

    _resv_buf: bytearray

    def __len__(self) -> int:
        return self._wpos - self._rpos

    def peek(self) -> memoryview:
        if self._rpos == self._wpos:
            return memoryview(b'')
        return memoryview(self._ba)[self._rpos:self._wpos]

    def segments(self) -> ta.Sequence[memoryview]:
        mv = self.peek()
        return (mv,) if len(mv) else ()

    def _check_no_reserve(self) -> None:
        if self._resv_start is not None:
            raise OutstandingReserveByteStreamBufferError('outstanding reserve')

    def write(self, data: BytesLike, /) -> None:
        self._check_no_reserve()
        if not data:
            return
        if isinstance(data, memoryview):
            data = data.tobytes()
        elif isinstance(data, bytearray):
            data = bytes(data)

        bl = len(data)

        if self._max_bytes is not None and len(self) + bl > self._max_bytes:
            raise BufferTooLargeByteStreamBufferError('buffer exceeded max_bytes')

        # Keep backing store "dense": if we've consumed everything, reset.
        if self._rpos == self._wpos and self._rpos:
            self._ba.clear()
            self._rpos = 0
            self._wpos = 0

        self._ba.extend(data)
        self._wpos += bl

    def reserve(self, n: int, /) -> memoryview:
        if n < 0:
            raise ValueError(n)
        if self._resv_start is not None:
            raise OutstandingReserveByteStreamBufferError('outstanding reserve')

        # Important: do NOT reserve by extending the backing bytearray and returning a view into it. A live exported
        # memoryview pins the bytearray against resizing, and commit() would need to shrink unused reservation space (or
        # otherwise reshape), which would raise BufferError.
        #
        # Instead, reserve returns a view of a temporary bytearray, and commit() appends only what was actually written.
        # This keeps reserve/commit safe and predictable.
        b = bytearray(n)
        self._resv_start = 0
        self._resv_len = n
        self._resv_buf = b
        return memoryview(b)

    def commit(self, n: int, /) -> None:
        if self._resv_start is None:
            raise NoOutstandingReserveByteStreamBufferError('no outstanding reserve')
        if n < 0 or n > self._resv_len:
            raise ValueError(n)

        b = self._resv_buf
        self._resv_start = None
        self._resv_len = 0
        del self._resv_buf

        if not n:
            return

        if self._max_bytes is not None and len(self) + n > self._max_bytes:
            raise BufferTooLargeByteStreamBufferError('buffer exceeded max_bytes')

        # Append only what was written.
        self.write(memoryview(b)[:n])

    def advance(self, n: int, /) -> None:
        self._check_no_reserve()
        if n < 0 or n > len(self):
            raise ValueError(n)
        if n == 0:
            return

        self._rpos += n

        # Compact opportunistically (content-preserving, may copy).
        # This avoids "huge buffer pinned by small tail" for contiguous backing.
        # Keep thresholds conservative to avoid excessive churn.
        if self._rpos and self._rpos >= 65536 and self._rpos >= (self._wpos // 2):
            del self._ba[:self._rpos]
            self._wpos -= self._rpos
            self._rpos = 0

        # Fully consumed: reset.
        if self._rpos == self._wpos:
            self._ba.clear()
            self._rpos = 0
            self._wpos = 0

    def split_to(self, n: int, /) -> SegmentedByteStreamBufferView:
        self._check_no_reserve()
        if n < 0 or n > len(self):
            raise ValueError(n)
        if n == 0:
            return SegmentedByteStreamBufferView(())

        # Copy out the split prefix to keep the view stable even if the underlying buffer compacts.
        b = bytes(memoryview(self._ba)[self._rpos:self._rpos + n])
        self._rpos += n

        if self._rpos == self._wpos:
            self._ba.clear()
            self._rpos = 0
            self._wpos = 0

        return SegmentedByteStreamBufferView((memoryview(b),))

    def find(self, sub: bytes, start: int = 0, end: ta.Optional[int] = None) -> int:
        start, end = self._norm_slice(start, end)
        if not sub:
            return start
        i = self._ba.find(sub, self._rpos + start, self._rpos + end)
        return -1 if i < 0 else (i - self._rpos)

    def rfind(self, sub: bytes, start: int = 0, end: ta.Optional[int] = None) -> int:
        start, end = self._norm_slice(start, end)
        if not sub:
            return end
        i = self._ba.rfind(sub, self._rpos + start, self._rpos + end)
        return -1 if i < 0 else (i - self._rpos)

    def coalesce(self, n: int, /) -> memoryview:
        self._check_no_reserve()
        if n < 0:
            raise ValueError(n)
        if n > len(self):
            raise ValueError(n)
        if n == 0:
            return memoryview(b'')
        # Always contiguous for the readable prefix.
        return memoryview(self._ba)[self._rpos:self._rpos + n]
