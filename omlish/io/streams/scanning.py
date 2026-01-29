# ruff: noqa: UP045
# @omlish-lite
import typing as ta

from .base import BaseByteStreamBufferLike
from .types import BytesLike
from .types import ByteStreamBufferView
from .types import MutableByteStreamBuffer


##


class ScanningByteStreamBuffer(BaseByteStreamBufferLike, MutableByteStreamBuffer):
    """
    A MutableByteStreamBuffer wrapper that caches negative-find progress to avoid repeated rescans in trickle scenarios.

    It is intentionally conservative:
      - It only caches progress for the default find range (start==0, end is None).
      - It only caches *negative* results (i.e., "-1"): once a match is found, caching is not updated, to preserve the
        property that repeated `find(sub)` on an unchanged buffer yields the same answer.

    This is designed to help framing-style code that repeatedly does:
      - buf.write(...small...)
      - buf.find(delim)
      - (not found) repeat
    """

    def __init__(self, buf) -> None:
        super().__init__()

        self._buf = buf
        self._scan_from_by_sub: dict[bytes, int] = {}

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
        self._adjust_for_consume(n)

    def split_to(self, n: int, /) -> ByteStreamBufferView:
        v = self._buf.split_to(n)
        self._adjust_for_consume(n)
        return v

    def coalesce(self, n: int, /) -> memoryview:
        return self._buf.coalesce(n)

    def find(self, sub: bytes, start: int = 0, end: ta.Optional[int] = None) -> int:
        if start != 0 or end is not None:
            return self._buf.find(sub, start, end)

        sub_len = len(sub)
        if sub_len <= 0:
            return self._buf.find(sub, start, end)

        scan_from = self._scan_from_by_sub.get(sub, 0)

        # Allow overlap so a match spanning old/new boundary is discoverable.
        overlap = sub_len - 1
        eff_start = scan_from - overlap
        if eff_start < 0:
            eff_start = 0

        i = self._buf.find(sub, eff_start, None)
        if i < 0:
            self._scan_from_by_sub[sub] = len(self._buf)

        return i

    def rfind(self, sub: bytes, start: int = 0, end: ta.Optional[int] = None) -> int:
        # rfind isn't the typical trickle hot-path; delegate.
        return self._buf.rfind(sub, start, end)

    #

    def write(self, data: BytesLike, /) -> None:
        self._buf.write(data)

    def reserve(self, n: int, /) -> memoryview:
        return self._buf.reserve(n)

    def commit(self, n: int, /) -> None:
        self._buf.commit(n)

    #

    def _adjust_for_consume(self, n: int) -> None:
        if not self._scan_from_by_sub:
            return

        if n <= 0:
            return

        # Only front-consumption exists in this buffer model.
        for k, v in list(self._scan_from_by_sub.items()):
            nv = v - n
            if nv <= 0:
                self._scan_from_by_sub.pop(k, None)
            else:
                self._scan_from_by_sub[k] = nv
