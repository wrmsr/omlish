# ruff: noqa: UP006 UP045
# @omlish-lite
import typing as ta

from omlish.lite.abstract import Abstract

from .types import ByteStreamBuffer


##


class BaseByteStreamBuffer(ByteStreamBuffer, Abstract):
    def _norm_slice(self, start: int, end: ta.Optional[int]) -> ta.Tuple[int, int]:
        length = len(self)

        if start < 0:
            start += length
        if start < 0:
            start = 0
        if start > length:
            start = length

        if end is None:
            end = length
        else:
            if end < 0:
                end += length
            if end < 0:
                end = 0
            if end > length:
                end = length

        if end < start:
            end = start

        return start, end
