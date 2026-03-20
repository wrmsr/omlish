import abc

from omlish import dataclasses as dc
from omlish import lang

from ...content.content import Content
from ..permissions.types import ToolPermissionTarget


##


class ToolExecutionError(Exception, lang.Abstract):
    @property
    @abc.abstractmethod
    def content(self) -> Content:
        raise NotImplementedError


@dc.dataclass()
class PermissionDeniedToolExecutionError(ToolExecutionError):
    target: ToolPermissionTarget

    @property
    def content(self) -> Content:
        return f'Tool execution permission denied for {self.target!r}.'
