# ruff: noqa: UP006 UP007 UP045
# @omlish-lite
import typing as ta

from .errors import BufferTooLarge
from .errors import NoOutstandingReserve
from .errors import OutstandingReserve
from .types import BytesLike
from .utils import _norm_slice


##


class SegmentedBytesView:
    """
    A read-only, possibly non-contiguous view over a sequence of byte segments.

    This is intended to be produced by `SegmentedBytesBuffer.split_to()` without copying.
    """

    def __init__(self, segs: ta.Sequence[memoryview]) -> None:
        super().__init__()

        self._segs = tuple(segs)
        for mv in self._segs:
            self._len += len(mv)

    _len = 0

    def __len__(self) -> int:
        return self._len

    def peek(self) -> memoryview:
        if not self._segs:
            return memoryview(b'')
        return self._segs[0]

    def segments(self) -> ta.Sequence[memoryview]:
        return self._segs

    def tobytes(self) -> bytes:
        if not self._segs:
            return b''
        if len(self._segs) == 1:
            return bytes(self._segs[0])
        return b''.join(bytes(mv) for mv in self._segs)


class SegmentedBytesBuffer:
    """
    A segmented, consumption-oriented bytes buffer.

    Internally stores a list of `bytes`/`bytearray` segments plus a head offset. Exposes readable data as `memoryview`
    segments without copying.

    Optional "chunked writes":
      - If chunk_size > 0, small writes are accumulated into a lazily-allocated active bytearray "chunk" up to
        chunk_size.
      - Writes >= chunk_size are stored as their own segments (after flushing any active chunk).
      - On flush, the active chunk is kept as a bytearray segment iff it is at least `chunk_compact_threshold` full;
        otherwise it is materialized as bytes to avoid pinning a large capacity for tiny content.

    Reserve/commit:
      - If chunk_size > 0 and reserve(n) fits in the active chunk, the reservation is carved from the active chunk.
        Reserved bytes are not readable until commit().
      - If reserve(n) does not fit, the active chunk is flushed first.
      - If n <= chunk_size after flushing, the reservation is served from a new active chunk (so the remainder becomes
        the next active chunk).
      - If n > chunk_size, reserve allocates a dedicated buffer and on commit it is "closed" (it does not become the
        next active chunk).

    Important exported-view caveat:
      - reserve() returns a memoryview. As long as any exported memoryview exists, the underlying bytearray must not be
        resized, or Python will raise BufferError. Therefore the active chunk bytearray is *fixed capacity*
        (len==chunk_size) and we track "used" bytes separately, writing via slice assignment rather than extend().
    """

    def __init__(
            self,
            *,
            max_bytes: ta.Optional[int] = None,
            chunk_size: int = 0,
            chunk_compact_threshold: float = .25,
    ) -> None:
        super().__init__()

        self._segs: ta.List[ta.Union[bytes, bytearray]] = []

        self._max_bytes = None if max_bytes is None else int(max_bytes)

        if chunk_size < 0:
            raise ValueError(chunk_size)
        self._chunk_size = chunk_size

        if not (0.0 <= chunk_compact_threshold <= 1.0):
            raise ValueError(chunk_compact_threshold)
        self._chunk_compact_threshold = chunk_compact_threshold

        self._active: ta.Optional[bytearray] = None
        self._active_used = 0

    _head_off = 0
    _len = 0

    _reserved: ta.Optional[bytearray] = None
    _reserved_len = 0
    _reserved_in_active = False

    def __len__(self) -> int:
        return self._len

    def _active_reserved_tail(self) -> int:
        if self._reserved_in_active and self._reserved is not None:
            return self._reserved_len
        return 0

    def _active_readable_len(self) -> int:
        if self._active is None:
            return 0
        tail = self._active_reserved_tail()
        rl = self._active_used - tail
        return rl if rl > 0 else 0

    def peek(self) -> memoryview:
        if not self._segs:
            return memoryview(b'')

        s0 = self._segs[0]
        mv = memoryview(s0)
        if self._head_off:
            mv = mv[self._head_off:]

        if self._active is not None and s0 is self._active:
            # Active is only meaningful by _active_used, not len(bytearray).
            rl = self._active_readable_len()
            if self._head_off >= rl:
                return memoryview(b'')
            mv = memoryview(self._active)[self._head_off:rl]
            return mv

        return mv

    def segments(self) -> ta.Sequence[memoryview]:
        if not self._segs:
            return ()

        out: ta.List[memoryview] = []

        last_i = len(self._segs) - 1
        for i, s in enumerate(self._segs):
            if self._active is not None and i == last_i and s is self._active:
                # Active chunk: create fresh view with readable length.
                rl = self._active_readable_len()
                if i == 0:
                    # Active is also first segment; apply head_off.
                    if self._head_off >= rl:
                        continue
                    mv = memoryview(self._active)[self._head_off:rl]
                else:
                    if rl <= 0:
                        continue
                    mv = memoryview(self._active)[:rl]
            else:
                # Non-active segment.
                mv = memoryview(s)
                if i == 0 and self._head_off:
                    mv = mv[self._head_off:]

            if len(mv):
                out.append(mv)

        return tuple(out)

    def _ensure_active(self) -> bytearray:
        if self._chunk_size <= 0:
            raise RuntimeError('no active chunk without chunk_size')

        a = self._active
        if a is None:
            a = bytearray(self._chunk_size)  # fixed capacity
            self._segs.append(a)
            self._active = a
            self._active_used = 0

        return a

    def _flush_active(self) -> None:
        if (a := self._active) is None:
            return

        if self._reserved_in_active:
            raise OutstandingReserve('outstanding reserve')

        if (used := self._active_used) <= 0:
            if self._segs and self._segs[-1] is a:
                self._segs.pop()
            self._active = None
            self._active_used = 0
            return

        # If under threshold, always bytes() to avoid pinning.
        if self._chunk_size and (float(used) / float(self._chunk_size)) < self._chunk_compact_threshold:
            if not self._segs or self._segs[-1] is not a:
                raise RuntimeError('active not at tail')
            self._segs[-1] = bytes(memoryview(a)[:used])

        else:
            # Try to shrink in-place to used bytes. If exported views exist, this can BufferError; fall back to bytes()
            # in that case.
            if not self._segs or self._segs[-1] is not a:
                raise RuntimeError('active not at tail')
            try:
                del a[used:]  # may raise BufferError if any exports exist
            except BufferError:
                self._segs[-1] = bytes(memoryview(a)[:used])

        self._active = None
        self._active_used = 0

    def write(self, data: BytesLike, /) -> None:
        if not data:
            return
        if isinstance(data, memoryview):
            data = data.tobytes()
        # elif isinstance(data, bytearray):
        #     pass
        # else:
        #     pass

        dl = len(data)

        if self._max_bytes is not None and self._len + dl > self._max_bytes:
            raise BufferTooLarge('buffer exceeded max_bytes')

        if self._chunk_size <= 0:
            self._segs.append(data)
            self._len += dl
            return

        if self._reserved_in_active:
            raise OutstandingReserve('outstanding reserve')

        if dl >= self._chunk_size:
            self._flush_active()
            self._segs.append(data)
            self._len += dl
            return

        a = self._ensure_active()
        if self._active_used + dl > self._chunk_size:
            self._flush_active()
            a = self._ensure_active()

        # Copy into fixed-capacity buffer; do not resize.
        memoryview(a)[self._active_used:self._active_used + dl] = data
        self._active_used += dl
        self._len += dl

    def reserve(self, n: int, /) -> memoryview:
        if n < 0:
            raise ValueError(n)
        if self._reserved is not None:
            raise OutstandingReserve('outstanding reserve')

        if self._chunk_size <= 0:
            b = bytearray(n)
            self._reserved = b
            self._reserved_len = n
            self._reserved_in_active = False
            return memoryview(b)

        if n > self._chunk_size:
            self._flush_active()
            b = bytearray(n)
            self._reserved = b
            self._reserved_len = n
            self._reserved_in_active = False
            return memoryview(b)

        # Ensure reservation fits in active; otherwise flush then create a new one.
        if self._active is not None and (self._active_used + n > self._chunk_size):
            self._flush_active()

        a = self._ensure_active()

        start = self._active_used
        # Reservation does not change _active_used (not readable until commit).
        self._reserved = a
        self._reserved_len = n
        self._reserved_in_active = True
        return memoryview(a)[start:start + n]

    def commit(self, n: int, /) -> None:
        if self._reserved is None:
            raise NoOutstandingReserve('no outstanding reserve')
        if n < 0 or n > self._reserved_len:
            raise ValueError(n)

        if self._reserved_in_active:
            a = self._reserved
            self._reserved = None
            self._reserved_len = 0
            self._reserved_in_active = False

            if self._max_bytes is not None and self._len + n > self._max_bytes:
                raise BufferTooLarge('buffer exceeded max_bytes')

            if n:
                self._active_used += n
                self._len += n

            # Keep active for reuse.
            self._active = a
            return

        b = self._reserved
        self._reserved = None
        self._reserved_len = 0
        self._reserved_in_active = False

        if self._max_bytes is not None and self._len + n > self._max_bytes:
            raise BufferTooLarge('buffer exceeded max_bytes')

        if not n:
            return

        if n == len(b):
            self._segs.append(b)
            self._len += n
        else:
            bb = bytes(memoryview(b)[:n])
            self._segs.append(bb)
            self._len += n

    def advance(self, n: int, /) -> None:
        if n < 0 or n > self._len:
            raise ValueError(n)
        if n == 0:
            return

        self._len -= n

        while n and self._segs:
            s0 = self._segs[0]

            if self._active is not None and s0 is self._active:
                avail0 = self._active_readable_len() - self._head_off
            else:
                avail0 = len(s0) - self._head_off

            if avail0 <= 0:
                popped = self._segs.pop(0)
                if popped is self._active:
                    self._active = None
                    self._active_used = 0
                self._head_off = 0
                continue

            if n < avail0:
                self._head_off += n
                return

            n -= avail0
            popped = self._segs.pop(0)
            if popped is self._active:
                self._active = None
                self._active_used = 0
            self._head_off = 0

        if n:
            raise RuntimeError(n)

    def split_to(self, n: int, /) -> SegmentedBytesView:
        if n < 0 or n > self._len:
            raise ValueError(n)
        if n == 0:
            return SegmentedBytesView(())

        out: ta.List[memoryview] = []
        rem = n

        while rem:
            if not self._segs:
                raise RuntimeError(rem)

            s0 = self._segs[0]

            if self._active is not None and s0 is self._active:
                rl = self._active_readable_len()
                if self._head_off >= rl:
                    raise RuntimeError(rem)
                mv0 = memoryview(s0)[self._head_off:rl]
            else:
                mv0 = memoryview(s0)
                if self._head_off:
                    mv0 = mv0[self._head_off:]

            if rem < len(mv0):
                out.append(mv0[:rem])
                self._head_off += rem
                self._len -= n
                return SegmentedBytesView(out)

            out.append(mv0)
            rem -= len(mv0)
            popped = self._segs.pop(0)
            if popped is self._active:
                self._active = None
                self._active_used = 0
            self._head_off = 0

        self._len -= n
        return SegmentedBytesView(out)

    def coalesce(self, n: int, /) -> memoryview:
        if n < 0:
            raise ValueError(n)
        if n > self._len:
            raise ValueError(n)
        if n == 0:
            return memoryview(b'')

        if self._reserved is not None:
            raise OutstandingReserve('outstanding reserve')

        mv0 = self.peek()
        if len(mv0) >= n:
            return mv0[:n]

        out = bytearray(n)
        w = 0

        new_segs: ta.List[ta.Union[bytes, bytearray]] = []

        seg_i = 0
        while w < n and seg_i < len(self._segs):
            s = self._segs[seg_i]
            off = self._head_off if seg_i == 0 else 0

            seg_len = len(s) - off
            if self._active is not None and seg_i == (len(self._segs) - 1) and s is self._active:
                seg_len = self._active_readable_len() - off

            if seg_len <= 0:
                seg_i += 1
                continue

            take = n - w
            if take > seg_len:
                take = seg_len

            out[w:w + take] = memoryview(s)[off:off + take]
            w += take

            if take < seg_len:
                rem = s[off + take:off + seg_len]
                if rem:
                    new_segs.append(rem)
                seg_i += 1
                break

            seg_i += 1

        if seg_i < len(self._segs):
            new_segs.extend(self._segs[seg_i:])

        self._segs = [bytes(out), *new_segs]
        self._head_off = 0

        self._active = None
        self._active_used = 0

        return memoryview(self._segs[0])[:n]

    def find(self, sub: bytes, start: int = 0, end: ta.Optional[int] = None) -> int:
        start, end = _norm_slice(len(self), start, end)

        m = len(sub)
        if m == 0:
            return start
        if end - start < m:
            return -1

        limit = end - m

        tail = b''
        tail_gstart = 0

        gpos = 0

        last_i = len(self._segs) - 1

        for si, s in enumerate(self._segs):
            off = self._head_off if si == 0 else 0

            seg_len = len(s) - off
            if self._active is not None and si == last_i and s is self._active:
                seg_len = self._active_readable_len() - off

            if seg_len <= 0:
                continue

            seg_gs = gpos
            seg_ge = gpos + seg_len

            if limit >= seg_gs and start < seg_ge:
                ls = start - seg_gs if start > seg_gs else 0
                max_start_in_seg = limit - seg_gs
                end_search = max_start_in_seg + m
                if end_search > seg_len:
                    end_search = seg_len
                if ls < end_search:
                    idx = s.find(sub, off + ls, off + end_search)
                    if idx != -1:
                        return seg_gs + (idx - off)

            if m > 1 and tail:
                head_need = m - 1
                head = s[off:off + head_need]
                comb = tail + head
                j = comb.find(sub)
                if j != -1 and j < len(tail) < j + m:
                    cand = tail_gstart + j
                    if start <= cand <= limit:
                        return cand

            if m > 1:
                take = m - 1
                if seg_len >= take:
                    tail = s[off + seg_len - take:off + seg_len]
                    tail_gstart = seg_ge - take
                else:
                    tail = (tail + s[off:off + seg_len])[-(m - 1):]
                    tail_gstart = seg_ge - len(tail)

            gpos = seg_ge

        return -1

    def rfind(self, sub: bytes, start: int = 0, end: ta.Optional[int] = None) -> int:
        start, end = _norm_slice(len(self), start, end)

        m = len(sub)
        if m == 0:
            return end
        if end - start < m:
            return -1

        limit = end - m

        if not self._segs:
            return -1

        best = -1

        seg_ge = self._len
        prev_s: ta.Optional[ta.Union[bytes, bytearray]] = None
        prev_off = 0

        last_i = len(self._segs) - 1

        for si in range(len(self._segs) - 1, -1, -1):
            s = self._segs[si]
            off = self._head_off if si == 0 else 0

            seg_len = len(s) - off
            if self._active is not None and si == last_i and s is self._active:
                seg_len = self._active_readable_len() - off

            if seg_len <= 0:
                continue

            seg_gs = seg_ge - seg_len

            if limit >= seg_gs and start < seg_ge:
                ls = start - seg_gs if start > seg_gs else 0
                max_start_in_seg = limit - seg_gs
                end_search = max_start_in_seg + m
                if end_search > seg_len:
                    end_search = seg_len
                if ls < end_search:
                    idx = s.rfind(sub, off + ls, off + end_search)
                    if idx != -1:
                        cand = seg_gs + (idx - off)
                        if cand > best:
                            best = cand

            if m > 1 and prev_s is not None:
                tail_need = m - 1
                if seg_len >= tail_need:
                    tail = s[off + seg_len - tail_need:off + seg_len]
                    tail_gstart = seg_ge - tail_need

                else:
                    tail_parts = [s[off:off + seg_len]]
                    tail_len = seg_len
                    for sj in range(si - 1, -1, -1):
                        if tail_len >= tail_need:
                            break

                        sj_s = self._segs[sj]
                        sj_off = self._head_off if sj == 0 else 0
                        sj_len = len(sj_s) - sj_off
                        if self._active is not None and sj == last_i and sj_s is self._active:
                            sj_len = self._active_readable_len() - sj_off
                        if sj_len <= 0:
                            continue

                        take = min(tail_need - tail_len, sj_len)
                        tail_parts.insert(0, sj_s[sj_off + sj_len - take:sj_off + sj_len])
                        tail_len += take

                    tail_combined = b''.join(tail_parts)
                    tail = tail_combined[-(m - 1):] if len(tail_combined) >= m - 1 else tail_combined
                    tail_gstart = seg_ge - len(tail)

                head_need = m - 1
                head = prev_s[prev_off:prev_off + head_need]

                comb = tail + head
                j = comb.rfind(sub)
                if j != -1 and j < len(tail) < j + m:
                    cand = tail_gstart + j
                    if start <= cand <= limit and cand > best:
                        best = cand

            if best >= seg_gs:
                return best

            prev_s = s
            prev_off = off
            seg_ge = seg_gs

        return best
