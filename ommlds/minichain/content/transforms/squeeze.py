import typing as ta

from omlish import dataclasses as dc
from omlish import dispatch

from ..sequence import SequenceContent
from ..text import TextContent
from ..types import Content
from ..types import SingleContent


##


class ContentSqueezer:
    def __init__(
            self,
            *,
            strip_strings: bool = False,
    ) -> None:
        super().__init__()

        self._strip_strings = strip_strings

    @dispatch.method()
    def squeeze(self, c: Content) -> ta.Iterable[SingleContent]:
        raise TypeError(c)

    #

    @squeeze.register
    def squeeze_str(self, c: str) -> ta.Iterable[SingleContent]:
        if self._strip_strings:
            c = c.strip()

        if c:
            yield c

    @squeeze.register
    def squeeze_sequence(self, c: ta.Sequence) -> ta.Iterable[SingleContent]:
        for e in c:
            yield from self.squeeze(e)

    #

    @squeeze.register
    def squeeze_single_content(self, c: SingleContent) -> ta.Iterable[SingleContent]:
        return [c]

    @squeeze.register
    def squeeze_text_content(self, c: TextContent) -> ta.Iterable[SingleContent]:
        if self._strip_strings:
            if (ss := c.s.strip()) != c.s:
                c = dc.replace(c, s=ss)

        if c.s:
            yield c.s

    @squeeze.register
    def squeeze_sequence_content(self, c: SequenceContent) -> ta.Iterable[SingleContent]:
        for e in c.l:
            yield from self.squeeze(e)


def squeeze_content(
        c: Content,
        *,
        strip_strings: bool = False,
) -> ta.Sequence[SingleContent]:
    return list(ContentSqueezer(
        strip_strings=strip_strings,
    ).squeeze(c))
