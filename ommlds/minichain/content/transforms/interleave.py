import typing as ta

from omlish import dataclasses as dc
from omlish import dispatch
from omlish import lang

from ..list import ListContent
from ..types import Content


##


class ContentInterleaver:
    def __init__(
            self,
            separator: Content,
    ) -> None:
        super().__init__()

        self._separator = separator

    @dispatch.method
    def interleave(self, c: Content) -> Content:
        return c

    @interleave.register
    def interleave_str(self, c: str) -> Content:
        return c

    @interleave.register
    def interleave_sequence(self, c: ta.Sequence) -> Content:
        return list(lang.interleave(map(self.interleave, c), self._separator))

    @interleave.register
    def interleave_list(self, c: ListContent) -> Content:
        return dc.replace(c, l=list(lang.interleave(map(self.interleave, c.l), self._separator)))


def interleave_content(c: Content, separator: Content) -> Content:
    return ContentInterleaver(
        separator=separator,
    ).interleave(c)
