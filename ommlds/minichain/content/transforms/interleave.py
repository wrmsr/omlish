import typing as ta

from omlish import dataclasses as dc
from omlish import dispatch
from omlish import lang

from ..sequence import BlockContent
from ..sequence import InlineContent
from ..types import Content


##


class ContentInterleaver:
    def __init__(
            self,
            *,
            separator: Content | None = None,
            sequence_separator: Content | None = None,
            inline_separator: Content | None = None,
            block_separator: Content | None = None,
    ) -> None:
        super().__init__()

        self._sequence_separator = sequence_separator if sequence_separator is not None else separator
        self._inline_separator = inline_separator if inline_separator is not None else separator
        self._block_separator = block_separator if block_separator is not None else separator

    def _interleave(self, l: ta.Iterable[Content], separator: Content | None) -> ta.Sequence[Content]:
        cs: ta.Iterable[Content] = map(self.interleave, l)
        if separator is not None:
            cs = lang.interleave(cs, separator)
        return list(cs)

    @dispatch.method()
    def interleave(self, c: Content) -> Content:
        return c

    @interleave.register
    def interleave_str(self, c: str) -> Content:
        return c

    @interleave.register
    def interleave_sequence(self, c: ta.Sequence) -> Content:
        return self._interleave(c, self._sequence_separator)

    @interleave.register
    def interleave_inline_content(self, c: InlineContent) -> Content:
        return dc.replace(c, l=self._interleave(c.l, self._inline_separator))

    @interleave.register
    def interleave_block_content(self, c: BlockContent) -> Content:
        return dc.replace(c, l=self._interleave(c.l, self._block_separator))


def interleave_content(
        c: Content,
        *,
        separator: Content | None = None,
        sequence_separator: Content | None = None,
        inline_separator: Content | None = None,
        block_separator: Content | None = None,
) -> Content:
    return ContentInterleaver(
        separator=separator,
        sequence_separator=sequence_separator,
        inline_separator=inline_separator,
        block_separator=block_separator,
    ).interleave(c)
