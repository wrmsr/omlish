import collections.abc

from omlish import dataclasses as dc
from omlish import dispatch
from omlish import lang

from ..quote import QuoteContent
from ..section import SectionContent
from ..sequence import SequenceContent
from ..types import Content
from ..types import LeafContent
from ..tag import TagContent


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
    def apply_sequence(self, l: collections.abc.Sequence[Content]) -> collections.abc.Sequence[Content]:
        return [self.apply(e) for e in l]

    #

    @apply.register
    def apply_leaf_content(self, c: LeafContent) -> LeafContent:
        return c

    @apply.register
    def apply_quote_content(self, c: QuoteContent) -> QuoteContent:
        return dc.replace(c, l=self.apply(c.body))

    @apply.register
    def apply_section_content(self, c: SectionContent) -> SectionContent:
        return dc.replace(c, l=self.apply(c.body))

    @apply.register
    def apply_sequence_content(self, c: SequenceContent) -> SequenceContent:
        return dc.replace(c, l=self.apply(c.l))

    @apply.register
    def apply_tag_content(self, c: TagContent) -> TagContent:
        return dc.replace(c, c=self.apply(c.body))
