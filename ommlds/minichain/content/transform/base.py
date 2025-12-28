import collections.abc

from omlish import dataclasses as dc
from omlish import dispatch
from omlish import lang

from ..quote import QuoteContent
from ..section import SectionContent
from ..sequence import SequenceContent
from ..tag import TagContent
from ..text import TextContent
from ..types import Content
from ..types import LeafContent


##


class ContentTransform(lang.Abstract):
    @dispatch.method()
    def apply(self, o: Content) -> Content:
        raise TypeError(o)

    #

    @apply.register  # noqa
    def apply_str(self, s: str) -> str:
        return s

    @apply.register  # noqa
    def apply_sequence(self, l: collections.abc.Sequence) -> collections.abc.Sequence:
        # FIXME: this should be `Sequence[Content] -> Sequence[Content]` but omlish.reflect can't handle recursive
        #   ForwardRef's yet
        r = [self.apply(e) for e in l]
        if len(r) == len(l) and all(le is re for le, re in zip(l, r)):
            return l
        return r

    #

    @apply.register
    def apply_leaf_content(self, c: LeafContent) -> LeafContent:
        return c

    @apply.register
    def apply_quote_content(self, c: QuoteContent) -> QuoteContent:
        return dc.replace_is_not(c, l=self.apply(c.body))

    @apply.register
    def apply_section_content(self, c: SectionContent) -> SectionContent:
        return dc.replace_is_not(c, l=self.apply(c.body))

    @apply.register
    def apply_sequence_content(self, c: SequenceContent) -> SequenceContent:
        return dc.replace_is_not(c, l=self.apply(c.l))

    @apply.register
    def apply_tag_content(self, c: TagContent) -> TagContent:
        return dc.replace_is_not(c, c=self.apply(c.body))

    @apply.register
    def apply_text_content(self, c: TextContent) -> TextContent:
        return dc.replace_is_not(c, s=self.apply(c.s))
