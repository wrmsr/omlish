import abc
import typing as ta

from omlish import lang

from ..content import Content


C = ta.TypeVar('C')


##


class ContentTransform(lang.Abstract, ta.Generic[C]):
    @abc.abstractmethod
    def transform(self, c: Content, ctx: C) -> Content:
        raise NotImplementedError
