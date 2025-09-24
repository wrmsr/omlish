import abc

from omlish import lang

from ...content.materialize import CanContent


##


class ToolExecutionError(Exception, lang.Abstract):
    @property
    @abc.abstractmethod
    def content(self) -> CanContent:
        raise NotImplementedError
