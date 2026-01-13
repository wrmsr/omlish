# ruff: noqa: UP045
# @omlish-lite
import typing as ta

from .linear import LinearBytesBuffer
from .segmented import SegmentedBytesBuffer
from .types import MutableBytesBuffer


##


class SpillingBytesBuffer:
    """
    A MutableBytesBuffer that starts as a linear bytearray-backed buffer and "spills" into a segmented buffer once it
    grows beyond a threshold.

    This is meant to keep the pathological 1-byte trickle case cheap (fast linear writes + fast contiguous finds) while
    still avoiding long-lived huge linear buffers pinned by tiny tails.

    Notes:
      - Spill is a one-way transition.
      - Spill currently materializes the readable bytes once (copy) as part of the transition; after that, segmentation
        avoids further large copies.
    """

    def __init__(
            self,
            *,
            initial_capacity: int = 64 * 1024,
            spill_threshold: int = 256 * 1024,
    ) -> None:
        super().__init__()

        self._spill_threshold = int(spill_threshold)

        # We don't assume ctor signatures of existing buffers; try a couple common shapes.
        try:
            self._buf = LinearBytesBuffer(initial_capacity=initial_capacity)
        except TypeError:
            try:
                self._buf = LinearBytesBuffer(initial_capacity)  # type: ignore[misc]
            except TypeError:
                self._buf = LinearBytesBuffer()

        self._spilled = False

    _buf: MutableBytesBuffer

    #

    def __len__(self) -> int:
        return len(self._buf)

    def peek(self) -> memoryview:
        return self._buf.peek()

    def segments(self) -> ta.Sequence[memoryview]:
        return self._buf.segments()

    #

    def advance(self, n: int, /) -> None:
        self._buf.advance(n)

    def split_to(self, n: int, /):
        return self._buf.split_to(n)

    def find(self, sub: bytes, start: int = 0, end: ta.Optional[int] = None) -> int:
        return self._buf.find(sub, start, end)

    def rfind(self, sub: bytes, start: int = 0, end: ta.Optional[int] = None) -> int:
        return self._buf.rfind(sub, start, end)

    #

    def write(self, data, /) -> None:
        self._buf.write(data)
        self._maybe_spill()

    def reserve(self, n: int, /) -> memoryview:
        return self._buf.reserve(n)

    def commit(self, n: int, /) -> None:
        self._buf.commit(n)
        self._maybe_spill()

    #

    def _maybe_spill(self) -> None:
        if self._spilled:
            return

        if len(self._buf) <= self._spill_threshold:
            return

        # One-way spill from linear -> segmented.
        sb = SegmentedBytesBuffer()

        if len(self._buf):
            # We accept a one-time copy cost at spill to keep the interface unchanged.
            v = self._buf.split_to(len(self._buf))
            sb.write(v.tobytes())

        self._buf = sb
        self._spilled = True
