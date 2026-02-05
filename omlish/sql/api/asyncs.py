import contextlib
import typing as ta

from ... import lang
from .adapters import Adapter
from .columns import Columns
from .core import AsyncConn
from .core import AsyncDb
from .core import AsyncRows
from .core import AsyncTransaction
from .core import Conn
from .core import Db
from .core import Rows
from .core import Transaction
from .queries import Queryable
from .rows import Row


T = ta.TypeVar('T')
P = ta.ParamSpec('P')


##


class Runner(ta.Protocol):
    def __call__(self, fn: ta.Callable[P, T], *args: P.args, **kwargs: P.kwargs) -> ta.Awaitable[T]: ...


@ta.final
class _RunnerContextManager:
    def __init__(self, runner: Runner, fn: ta.Callable, wrapper: ta.Any) -> None:
        self._runner = runner
        self._fn = fn
        self._wrapper = wrapper

    _cm: ta.Any

    async def __aenter__(self):
        self._cm = await self._runner(self._fn)
        return self._wrapper(self._runner, await self._runner(self._cm.__enter__))

    async def __aexit__(self, et, e, tb):
        return await self._runner(self._cm.__exit__, et, e, tb)


##


class _RunnerStopIteration(lang.Marker):
    pass


class SyncToAsyncRows(AsyncRows):
    def __init__(self, runner: Runner, rows: Rows) -> None:
        super().__init__()

        self._runner = runner
        self._rows = rows

    @property
    def columns(self) -> Columns:
        return self._rows.columns

    async def __anext__(self) -> Row:  # ta.Raises[StopIteration]
        def inner():
            try:
                return self._rows.__next__()
            except StopIteration:
                return _RunnerStopIteration

        if (v := await self._runner(inner)) is _RunnerStopIteration:
            raise StopAsyncIteration

        return v


class SyncToAsyncTransaction(AsyncTransaction):
    def __init__(self, runner: Runner, txn: Transaction) -> None:
        super().__init__()

        self._runner = runner
        self._txn = txn

    @property
    def adapter(self) -> Adapter:
        return self._txn.adapter

    async def commit(self) -> None:
        return await self._runner(self._txn.commit)

    async def rollback(self) -> None:
        return await self._runner(self._txn.rollback)

    def query(self, query: Queryable) -> ta.AsyncContextManager[AsyncRows]:  # ta.Raises[QueryError]
        return _RunnerContextManager(self._runner, lambda: self._txn.query(query), SyncToAsyncRows)


class SyncToAsyncConn(AsyncConn):
    def __init__(self, runner: Runner, conn: Conn) -> None:
        super().__init__()

        self._runner = runner
        self._conn = conn

    @property
    def adapter(self) -> Adapter:
        return self._conn.adapter

    def begin(self) -> ta.AsyncContextManager[AsyncTransaction]:
        return _RunnerContextManager(self._runner, self._conn.begin, SyncToAsyncTransaction)

    def query(self, query: Queryable) -> ta.AsyncContextManager[AsyncRows]:  # ta.Raises[QueryError]
        return _RunnerContextManager(self._runner, lambda: self._conn.query(query), SyncToAsyncRows)


class SyncToAsyncDb(AsyncDb):
    def __init__(
            self,
            runner_factory: ta.Callable[[], ta.AsyncContextManager[Runner]],
            db: Db,
    ) -> None:
        super().__init__()

        self._runner_factory = runner_factory
        self._db = db

    @property
    def adapter(self) -> Adapter:
        return self._db.adapter

    async def _connect(self, aes: contextlib.AsyncExitStack) -> AsyncConn:
        runner = await aes.enter_async_context(self._runner_factory())

        rcm = _RunnerContextManager(runner, self._db.connect, SyncToAsyncConn)
        return await aes.enter_async_context(rcm)

    def connect(self) -> ta.AsyncContextManager[AsyncConn]:
        @contextlib.asynccontextmanager
        async def inner():
            async with contextlib.AsyncExitStack() as aes:
                yield await self._connect(aes)

        return inner()

    def query(self, query: Queryable) -> ta.AsyncContextManager[AsyncRows]:  # ta.Raises[QueryError]
        @contextlib.asynccontextmanager
        async def inner():
            async with contextlib.AsyncExitStack() as aes:
                conn = await self._connect(aes)
                yield await aes.enter_async_context(conn.query(query))

        return inner()
