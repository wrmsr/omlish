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
    """

    def __init__(self, *, max_bytes: ta.Optional[int] = None) -> None:
        super().__init__()

        self._segs: ta.List[ta.Union[bytes, bytearray]] = []

        self._max_bytes = None if max_bytes is None else int(max_bytes)

    _head_off = 0
    _len = 0

    _reserved: ta.Optional[bytearray] = None
    _reserved_len = 0

    def __len__(self) -> int:
        return self._len

    def peek(self) -> memoryview:
        if not self._segs:
            return memoryview(b'')
        s0 = self._segs[0]
        mv = memoryview(s0)
        if self._head_off:
            mv = mv[self._head_off:]
        return mv

    def segments(self) -> ta.Sequence[memoryview]:
        if not self._segs:
            return ()
        out: ta.List[memoryview] = []
        for i, s in enumerate(self._segs):
            mv = memoryview(s)
            if i == 0 and self._head_off:
                mv = mv[self._head_off:]
            if len(mv):
                out.append(mv)
        return tuple(out)

    def write(self, data: BytesLike, /) -> None:
        if not data:
            return
        if isinstance(data, memoryview):
            # Avoid holding onto a potentially huge exporting object; materialize as bytes. Callers that want zero-copy
            # should prefer reserve/commit for mutable storage.
            data = data.tobytes()
        elif isinstance(data, bytearray):
            # Keep as-is; memoryview(bytearray) is a non-copying view for readers.
            pass
        else:
            # bytes
            pass

        dl = len(data)

        if self._max_bytes is not None and self._len + dl > self._max_bytes:
            raise BufferTooLarge('buffer exceeded max_bytes')

        self._segs.append(data)
        self._len += dl

    def reserve(self, n: int, /) -> memoryview:
        if n < 0:
            raise ValueError(n)
        if self._reserved is not None:
            raise OutstandingReserve('outstanding reserve')
        b = bytearray(n)
        self._reserved = b
        self._reserved_len = n
        return memoryview(b)

    def commit(self, n: int, /) -> None:
        if self._reserved is None:
            raise NoOutstandingReserve('no outstanding reserve')
        if n < 0 or n > self._reserved_len:
            raise ValueError(n)

        if self._max_bytes is not None and self._len + n > self._max_bytes:
            # Keep reservation state consistent: drop reservation before raising.
            self._reserved = None
            self._reserved_len = 0
            raise BufferTooLarge('buffer exceeded max_bytes')

        b = self._reserved
        self._reserved = None
        self._reserved_len = 0
        if n:
            if n == len(b):
                self._segs.append(b)
                self._len += n
            else:
                # Copy only what caller actually wrote; drop unused tail to avoid pinning.
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
            avail0 = len(s0) - self._head_off
            if n < avail0:
                self._head_off += n
                return

            n -= avail0
            self._segs.pop(0)
            self._head_off = 0

        if n:
            # Should be impossible given bounds check above.
            raise AssertionError(n)

    def split_to(self, n: int, /) -> SegmentedBytesView:
        if n < 0 or n > self._len:
            raise ValueError(n)
        if n == 0:
            return SegmentedBytesView(())

        out: ta.List[memoryview] = []
        rem = n

        while rem:
            if not self._segs:
                raise AssertionError(rem)

            s0 = self._segs[0]
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
            self._segs.pop(0)
            self._head_off = 0

        self._len -= n
        return SegmentedBytesView(out)

    def coalesce(self, n: int, /) -> memoryview:
        """
        Ensure the first `n` readable bytes are available contiguously and return a view of them.

        Semantics:
          - Non-consuming: does not advance.
          - May restructure internal segments (content-preserving) to make the prefix contiguous.
          - Returns a read-only-ish `memoryview` (callers must not mutate readable bytes).

        Copying behavior:
          - If `peek()` already exposes >= n contiguous bytes, this is zero-copy.
          - Otherwise, it copies exactly the first `n` bytes into a new contiguous segment and rewrites the internal
            segment list so that segment[0] contains that prefix.

        Reserve interaction:
          - Disallowed while an outstanding reservation exists, since reserve() hands out a view that must not be
            invalidated by internal reshaping.
        """

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

        # Copy the minimal prefix required, then rebuild the head of the segment list.
        out = bytearray(n)
        w = 0

        new_segs: ta.List[ta.Union[bytes, bytearray]] = []

        seg_i = 0
        while w < n and seg_i < len(self._segs):
            s = self._segs[seg_i]
            off = self._head_off if seg_i == 0 else 0
            avail = len(s) - off
            if avail <= 0:
                seg_i += 1
                continue

            take = n - w
            if take > avail:
                take = avail

            out[w:w + take] = memoryview(s)[off:off + take]
            w += take

            if take < avail:
                # Preserve the remainder of this segment after the coalesced prefix.
                # Note: for bytes/bytearray, slicing copies. This avoids pinning a huge backing store via offsets, but
                # could copy a large tail; we may revisit this tradeoff in future backends.
                rem = s[off + take:off + avail]
                if rem:
                    new_segs.append(rem)
                seg_i += 1
                break

            seg_i += 1

        # Append any remaining segments after the portion we consumed into `out`.
        if seg_i < len(self._segs):
            new_segs.extend(self._segs[seg_i:])

        # Rebuild: coalesced prefix becomes the first segment; head offset resets.
        self._segs = [bytes(out), *new_segs]
        self._head_off = 0

        return memoryview(self._segs[0])[:n]

    def find(self, sub: bytes, start: int = 0, end: ta.Optional[int] = None) -> int:
        start, end = _norm_slice(len(self), start, end)

        m = len(sub)
        if m == 0:
            return start
        if end - start < m:
            return -1

        limit = end - m  # Last valid start offset for a match

        tail = b''  # Last (m-1) bytes before current segment
        tail_gstart = 0  # Global start offset of `tail`

        gpos = 0  # Global position of start of current segment's readable bytes
        for si, s in enumerate(self._segs):
            off = self._head_off if si == 0 else 0
            seg_len = len(s) - off
            if seg_len <= 0:
                continue

            seg_gs = gpos
            seg_ge = gpos + seg_len

            # In-segment search window for starts within [start, limit].
            if limit >= seg_gs and start < seg_ge:
                ls = start - seg_gs if start > seg_gs else 0
                # end_search ensures any match found starts <= limit
                max_start_in_seg = limit - seg_gs
                end_search = max_start_in_seg + m
                if end_search > seg_len:
                    end_search = seg_len
                if ls < end_search:
                    idx = s.find(sub, off + ls, off + end_search)
                    if idx != -1:
                        return seg_gs + (idx - off)

            # Boundary-crossing search using small window (tail + head).
            if m > 1 and tail:
                head_need = m - 1
                head = s[off:off + head_need]
                comb = tail + head
                j = comb.find(sub)
                if j != -1 and j < len(tail) < j + m:
                    cand = tail_gstart + j
                    if start <= cand <= limit:
                        return cand

            # Update rolling tail to last (m-1) bytes ending at seg end.
            if m > 1:
                take = m - 1
                if seg_len >= take:
                    tail = s[off + seg_len - take:off + seg_len]
                    tail_gstart = seg_ge - take
                else:
                    # Extend tail with entire segment, then keep only last (m-1).
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

        limit = end - m  # Last valid start offset for a match

        if not self._segs:
            return -1

        best = -1

        # Anchor at the end using self._len and work backwards.
        seg_ge = self._len
        prev_s: ta.Optional[ta.Union[bytes, bytearray]] = None
        prev_off = 0

        # Iterate segments right to left.
        for si in range(len(self._segs) - 1, -1, -1):
            s = self._segs[si]
            off = self._head_off if si == 0 else 0
            seg_len = len(s) - off
            if seg_len <= 0:
                continue

            seg_gs = seg_ge - seg_len

            # Within-segment search.
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

            # Boundary-crossing search with the previously-processed (rightward) segment.
            if m > 1 and prev_s is not None:
                # Tail: last (m-1) bytes ending at current segment end. If current segment is too small, lookahead
                # leftward to gather enough bytes.
                tail_need = m - 1
                if seg_len >= tail_need:
                    tail = s[off + seg_len - tail_need:off + seg_len]
                    tail_gstart = seg_ge - tail_need
                else:
                    # Segment too small; lookahead to gather tail bytes from left.
                    tail_parts = [s[off:off + seg_len]]
                    tail_len = seg_len
                    for sj in range(si - 1, -1, -1):
                        if tail_len >= tail_need:
                            break
                        sj_s = self._segs[sj]
                        sj_off = self._head_off if sj == 0 else 0
                        sj_len = len(sj_s) - sj_off
                        if sj_len <= 0:
                            continue
                        # Take bytes from end of segment sj.
                        take = min(tail_need - tail_len, sj_len)
                        tail_parts.insert(0, sj_s[sj_off + sj_len - take:sj_off + sj_len])
                        tail_len += take
                    tail_combined = b''.join(tail_parts)
                    tail = tail_combined[-(m - 1):] if len(tail_combined) >= m - 1 else tail_combined
                    tail_gstart = seg_ge - len(tail)

                # Head: first (m-1) bytes of next (right) segment.
                head_need = m - 1
                head = prev_s[prev_off:prev_off + head_need]

                comb = tail + head
                j = comb.rfind(sub)
                if j != -1 and j < len(tail) < j + m:
                    # Match crosses boundary.
                    cand = tail_gstart + j
                    if start <= cand <= limit and cand > best:
                        best = cand

            # Early termination: if we found any match at or after the start of this segment, no earlier segment can
            # contain a better (more rightward) match.
            if best >= seg_gs:
                return best

            # Save current segment info for next iteration (as the "previous" rightward segment).
            prev_s = s
            prev_off = off
            seg_ge = seg_gs

        return best
