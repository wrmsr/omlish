import typing as ta

from ..types import Content
from .base import ContentTransform


##


class ContentSqueezer(ContentTransform):
    def __init__(
            self,
            *,
            strip_strings: bool = False,
    ) -> None:
        super().__init__()

        self._strip_strings = strip_strings

    @ContentTransform.apply.register
    def squeeze_str(self, c: str) -> ta.Iterable[Content]:
        if self._strip_strings:
            c = c.strip()
        return c

    # @squeeze.register
    # def squeeze_sequence(self, c: ta.Sequence) -> ta.Iterable[Content]:
    #     for e in c:
    #         yield from self.squeeze(e)

    # #

    # # @squeeze.register
    # # def squeeze_single_content(self, c: Content) -> ta.Iterable[Content]:
    # #     return [c]

    # @squeeze.register
    # def squeeze_text_content(self, c: TextContent) -> ta.Iterable[Content]:
    #     if self._strip_strings:
    #         if (ss := c.s.strip()) != c.s:
    #             c = dc.replace(c, s=ss)
    #
    #     if c.s:
    #         yield c.s

    # @squeeze.register
    # def squeeze_sequence_content(self, c: SequenceContent) -> ta.Iterable[Content]:
    #     for e in c.l:
    #         yield from self.squeeze(e)


def squeeze_content(
        c: Content,
        *,
        strip_strings: bool = False,
) -> Content:
    return ContentSqueezer(
        strip_strings=strip_strings,
    ).apply(c)
