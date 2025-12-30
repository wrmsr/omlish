import abc

from omlish import lang

from ...content.content import Content


##


class ToolExecutionError(Exception, lang.Abstract):
    @property
    @abc.abstractmethod
    def content(self) -> Content:
        raise NotImplementedError
