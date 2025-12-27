import collections.abc
import typing as ta

from omlish import dataclasses as dc
from omlish import dispatch
from omlish import lang

from ..images import ImageContent
from ..sequence import SequenceContent
from ..text import TextContent


T = ta.TypeVar('T')


##


class ContentTransform(lang.Abstract):
    @dispatch.method(installable=True)
    def apply(self, o: T) -> T:
        raise TypeError(o)

    #

    @apply.register  # noqa
    def apply_str(self, s: str) -> str:
        return s

    @apply.register  # noqa
    def apply_sequence(self, l: collections.abc.Sequence[T]) -> collections.abc.Sequence[T]:
        return [self.apply(e) for e in l]

    #

    @apply.register
    def apply_image_content(self, c: ImageContent) -> ImageContent:
        return c

    @apply.register
    def apply_sequence_content(self, c: SequenceContent) -> SequenceContent:
        return dc.replace(c, l=self.apply(c.l))

    @apply.register
    def apply_text_content(self, c: TextContent) -> TextContent:
        return dc.replace(c, s=self.apply(c.s))
