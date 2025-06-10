import collections.abc
import typing as ta

from omlish import dataclasses as dc
from omlish import dispatch
from omlish import lang

from .images import ImageContent
from .list import ListContent
from .text import TextContent


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
    def apply_image(self, c: ImageContent) -> ImageContent:
        return c

    @apply.register
    def apply_list(self, c: ListContent) -> ListContent:
        return dc.replace(c, l=self.apply(c.l))

    @apply.register
    def apply_text(self, c: TextContent) -> ListContent:
        return dc.replace(c, s=self.apply(c.s))


##


@dc.dataclass(frozen=True)
class StringFnContentTransform(ContentTransform):
    fn: ta.Callable[[str], str]

    @ContentTransform.apply.register  # noqa
    def apply_str(self, s: str) -> str:
        return self.fn(s)


def transform_content_strings(fn: ta.Callable[[str], str], o: T) -> T:
    return StringFnContentTransform(fn).apply(o)
