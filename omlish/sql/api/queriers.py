import abc
import typing as ta

from ... import lang
from .adapters import HasAdapter
from .queries import Query


if ta.TYPE_CHECKING:
    from .core import Rows


##


class AnyQuerier(HasAdapter, lang.Abstract):
    pass


class Querier(AnyQuerier, lang.Abstract):
    @abc.abstractmethod
    def query(self, query: Query) -> ta.ContextManager['Rows']:  # ta.Raises[QueryError]
        raise NotImplementedError


class AsyncQuerier(AnyQuerier, lang.Abstract):
    @abc.abstractmethod
    def query(self, query: Query) -> ta.AsyncContextManager['Rows']:  # ta.Raises[QueryError]
        raise NotImplementedError
