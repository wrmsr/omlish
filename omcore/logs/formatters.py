import abc

from ..lite.abstract import Abstract
from .contexts import LoggingContext


##


class LoggingContextFormatter(Abstract):
    @abc.abstractmethod
    def format(self, ctx: LoggingContext) -> str:
        raise NotImplementedError
