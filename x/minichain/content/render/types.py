import abc
import typing as ta

from omlish import lang

from ..content import Content


R = ta.TypeVar('R')


##


class ContentRenderer(lang.Abstract, ta.Generic[R]):
    @abc.abstractmethod
    def render(self, c: Content) -> R:
        raise NotImplementedError


ContentStrRenderer: ta.TypeAlias = ContentRenderer[str]
