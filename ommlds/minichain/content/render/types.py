import abc

from omlish import lang

from ..content import Content


##


class ContentStrRenderer(lang.Abstract):
    @abc.abstractmethod
    def render(self, c: Content) -> str:
        raise NotImplementedError
