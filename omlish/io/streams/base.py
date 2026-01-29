# ruff: noqa: UP006 UP045
# @omlish-lite
import typing as ta

from ...lite.abstract import Abstract
from .types import ByteStreamBufferLike


##


class BaseByteStreamBufferLike(ByteStreamBufferLike, Abstract):
    def _norm_slice(self, start: int, end: ta.Optional[int]) -> ta.Tuple[int, int]:
        s, e, _ = slice(start, end, 1).indices(len(self))
        if e < s:
            e = s
        return s, e
