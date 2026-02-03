import abc
import typing as ta

from ... import check
from ... import lang
from .adapters import HasAdapter
from .queries import Query


if ta.TYPE_CHECKING:
    from .core import AsyncRows
    from .core import Rows


##


class AnyQuerier(HasAdapter, lang.Abstract):
    pass


class Querier(AnyQuerier, lang.Abstract):
    @abc.abstractmethod
    def query(self, query: Query) -> ta.ContextManager['Rows']:  # ta.Raises[QueryError]
        raise NotImplementedError

    def __init_subclass__(cls, **kwargs: ta.Any) -> None:
        super().__init_subclass__(**kwargs)

        try:
            aq = AsyncQuerier
        except NameError:
            pass
        else:
            check.not_issubclass(cls, aq)


class AsyncQuerier(AnyQuerier, lang.Abstract):
    @abc.abstractmethod
    def query(self, query: Query) -> ta.AsyncContextManager['AsyncRows']:  # ta.Raises[QueryError]
        raise NotImplementedError

    def __init_subclass__(cls, **kwargs: ta.Any) -> None:
        super().__init_subclass__(**kwargs)

        check.not_issubclass(cls, Querier)
