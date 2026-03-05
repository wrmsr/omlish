import abc
import typing as ta

from omlish import dataclasses as dc
from omlish import lang

from ..content import Content


##


class ContentTransform(lang.Abstract):
    @abc.abstractmethod
    def transform(self, c: Content) -> Content:
        raise NotImplementedError


##


@dc.dataclass(frozen=True)
class CompositeContentTransform(ContentTransform):
    cts: ta.Sequence[ContentTransform]

    def transform(self, c: Content) -> Content:
        for ct in self.cts:
            c = ct.transform(c)
        return c


@dc.dataclass(frozen=True)
class FnContentTransform(ContentTransform):
    fn: ta.Callable[[Content], Content]

    def transform(self, message: Content) -> Content:
        return self.fn(message)


@dc.dataclass(frozen=True)
class TypeFilteredContentTransform(ContentTransform):
    ty: type | tuple[type, ...]
    ct: ContentTransform

    def transform(self, c: Content) -> Content:
        if isinstance(c, self.ty):
            return self.ct.transform(c)
        else:
            return c
