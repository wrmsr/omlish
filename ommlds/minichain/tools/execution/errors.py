import abc

from omlish import lang

from ...content.types import Content


##


class ToolExecutionError(Exception, lang.Abstract):
    @property
    @abc.abstractmethod
    def content(self) -> Content:
        raise NotImplementedError
