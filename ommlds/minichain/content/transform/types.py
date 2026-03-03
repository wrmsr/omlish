import abc
import typing as ta

from omlish import dataclasses as dc
from omlish import lang

from ..content import Content


C = ta.TypeVar('C')


##


class ContentTransform(lang.Abstract, ta.Generic[C]):
    @abc.abstractmethod
    def transform(self, c: Content, ctx: C) -> Content:
        raise NotImplementedError


##


@dc.dataclass(frozen=True)
class FnContentTransform(ContentTransform[C]):
    fn: ta.Callable[[Content], Content]

    def transform(self, message: Content, ctx: C) -> Content:
        return self.fn(message)
