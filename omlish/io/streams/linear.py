# ruff: noqa: UP006 UP007 UP045
# @omlish-lite
import typing as ta

from .base import BaseByteStreamBufferLike
from .direct import _EMPTY_DIRECT_BYTE_STREAM_BUFFER_VIEW
from .direct import DirectByteStreamBufferView
from .errors import BufferTooLargeByteStreamBufferError
from .errors import NoOutstandingReserveByteStreamBufferError
from .errors import OutstandingReserveByteStreamBufferError
from .types import BytesLike
from .types import ByteStreamBufferView
from .types import MutableByteStreamBuffer


##


class LinearByteStreamBuffer(BaseByteStreamBufferLike, MutableByteStreamBuffer):
    """
    A simple contiguous (bytearray-backed) MutableByteStreamBuffer implementation.

    Strengths:
      - Fast `find/rfind` and contiguous peeking.
      - Efficient reserve/commit (safe against exported-memoryview resizing hazards).

    Tradeoffs:
      - `split_to` returns a stable view by copying the split bytes into an owned `bytes` object. (A truly zero-copy
        split view would require pinning the underlying bytearray against compaction.)
      - Compaction is best-effort: if the backing bytearray is pinned by exported memoryviews, compaction will be
        skipped and the buffer will remain correct but may retain memory.
    """

    def __init__(
            self,
            *,
            max_bytes: ta.Optional[int] = None,
            initial_capacity: int = 0,
            compact_threshold: int = 1 << 16,
    ) -> None:
        super().__init__()

        self._max_bytes = None if max_bytes is None else int(max_bytes)

        if initial_capacity < 0:
            raise ValueError(initial_capacity)
        if self._max_bytes is not None and initial_capacity > self._max_bytes:
            raise BufferTooLargeByteStreamBufferError('buffer exceeded max_bytes')

        if compact_threshold < 0:
            raise ValueError(compact_threshold)
        self._compact_threshold = int(compact_threshold)

        # Diagnostics (best-effort compaction behavior)
        self.compaction_attempts = 0
        self.compaction_successes = 0
        self.compaction_skipped_exports = 0

        # Pre-size the backing store to encourage fewer resizes/copies on trickle-y writes. We immediately clear so
        # readable length remains 0.
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

        # If buffer is logically empty but backing store might still be large (e.g. compaction skipped),
        # keep indices reset and just append.
        if self._rpos == self._wpos:
            self._rpos = 0
            self._wpos = 0
            # Best-effort shrink on empty: may be pinned, so ignore failure.
            self._try_clear_if_empty()

        self._ba.extend(data)
        self._wpos += bl

    def reserve(self, n: int, /) -> memoryview:
        if n < 0:
            raise ValueError(n)
        if self._resv_start is not None:
            raise OutstandingReserveByteStreamBufferError('outstanding reserve')

        # Do NOT reserve by extending the backing bytearray and returning a view into it: a live exported memoryview
        # pins the bytearray against resizing, and commit() would need to shrink unused reservation (or otherwise
        # reshape), which would raise BufferError.
        #
        # Instead, reserve returns a view of a temporary bytearray, and commit() appends only what was written.
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
        if not n:
            return

        self._rpos += n

        # Best-effort compaction (may skip if backing store is pinned by exported memoryviews).
        self.compact()

        # Fully consumed: reset indices and attempt to clear backing store best-effort.
        if self._rpos == self._wpos:
            self._rpos = 0
            self._wpos = 0
            self._try_clear_if_empty()

    def split_to(self, n: int, /) -> ByteStreamBufferView:
        self._check_no_reserve()
        if n < 0 or n > len(self):
            raise ValueError(n)
        if not n:
            return _EMPTY_DIRECT_BYTE_STREAM_BUFFER_VIEW

        # Copy out the split prefix to keep the view stable even if the underlying buffer compacts.
        b = bytes(memoryview(self._ba)[self._rpos:self._rpos + n])
        self._rpos += n

        # If we consumed everything, reset best-effort; otherwise allow compaction policy to handle later.
        if self._rpos == self._wpos:
            self._rpos = 0
            self._wpos = 0
            self._try_clear_if_empty()

        return DirectByteStreamBufferView(memoryview(b))

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
        if not n:
            return memoryview(b'')
        # Always contiguous for the readable prefix.
        return memoryview(self._ba)[self._rpos:self._rpos + n]

    def compact(
            self,
            *,
            threshold: ta.Optional[int] = None,
            min_fraction: float = 0.5,
            force: bool = False,
    ) -> bool:
        """
        Best-effort compaction to avoid "huge buffer pinned by small tail".

        Returns True if compaction happened, False otherwise.

        Compaction attempts to drop the consumed prefix of the backing bytearray by resizing it. If the bytearray is
        pinned by exported memoryviews, Python raises BufferError; in that case compaction is skipped (buffer remains
        correct) and the skip is recorded in diagnostics.

        Args:
          threshold: minimum consumed prefix size (bytes) required before compaction is considered. Defaults to the
                     instance's configured compact threshold (64KiB by default).
          min_fraction: require consumed prefix to be at least this fraction of the backing 'written' size. Defaults to
                        0.5 (i.e., consumed >= half of written region).
          force: if True, ignore heuristic checks and attempt compaction whenever `_rpos > 0`.

        Notes:
          - Compaction is disallowed while a reserve is outstanding.
          - Compaction is an optimization only; semantics do not depend on it.
        """

        self._check_no_reserve()

        if threshold is None:
            threshold = self._compact_threshold
        else:
            threshold = int(threshold)

        if not force:
            if self._rpos <= 0:
                return False
            if self._rpos < threshold:
                return False
            if self._wpos <= 0:
                return False
            if self._rpos < int(self._wpos * float(min_fraction)):
                return False
        else:
            if self._rpos <= 0:
                return False

        self.compaction_attempts += 1

        try:
            del self._ba[:self._rpos]
        except BufferError:
            self.compaction_skipped_exports += 1
            return False

        self._wpos -= self._rpos
        self._rpos = 0
        self.compaction_successes += 1
        return True

    def _try_clear_if_empty(self) -> None:
        """
        Best-effort clear of backing store when logically empty.

        If the backing store is pinned by exported memoryviews, clear will raise BufferError.
        In that case we keep the backing store allocated (correctness preserved) and move on.
        """

        if self._rpos != 0 or self._wpos != 0:
            return
        if not self._ba:
            return

        try:
            self._ba.clear()
        except BufferError:
            # Keep storage; callers wanted deterministic correctness over reclamation.
            pass
