import typing as ta

from .core import AsyncConn
from .core import AsyncDb
from .core import AsyncRows
from .core import AsyncTransaction
from .core import Conn
from .core import Db
from .core import Rows
from .core import Transaction
from .queries import Query
from .rows import Row


T = ta.TypeVar('T')

Runner: ta.TypeAlias = ta.Callable[[ta.Callable, T], ta.Awaitable[T]]


##


class SyncToAsyncRows(AsyncRows):
    def __init__(self, r: Runner, u: Rows) -> None:
        super().__init__()

        self._r = r
        self._u = u

    def __anext__(self) -> ta.Awaitable[Row]:  # ta.Raises[StopIteration]
        raise NotImplementedError


class SyncToAsyncTransaction(AsyncTransaction):
    def __init__(self, r: Runner, u: Transaction) -> None:
        super().__init__()

        self._r = r
        self._u = u

    async def commit(self) -> None:
        raise NotImplementedError

    async def rollback(self) -> None:
        raise NotImplementedError

    def query(self, query: Query) -> ta.AsyncContextManager[AsyncRows]:  # ta.Raises[QueryError]
        raise NotImplementedError


class SyncToAsyncConn(AsyncConn):
    def __init__(self, r: Runner, u: Conn) -> None:
        super().__init__()

        self._r = r
        self._u = u

    def begin(self) -> ta.AsyncContextManager[AsyncTransaction]:
        raise NotImplementedError

    def query(self, query: Query) -> ta.AsyncContextManager[AsyncRows]:  # ta.Raises[QueryError]
        raise NotImplementedError


class SyncToAsyncDb(AsyncDb):
    def __init__(self, r: Runner, u: Db) -> None:
        super().__init__()

        self._r = r
        self._u = u

    def connect(self) -> ta.AsyncContextManager[AsyncConn]:
        raise NotImplementedError

    def query(self, query: Query) -> ta.AsyncContextManager[AsyncRows]:  # ta.Raises[QueryError]
        raise NotImplementedError
