import contextlib
import sys
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
from .queries import Query
from .rows import Row


T = ta.TypeVar('T')
P = ta.ParamSpec('P')


##


class Runner(ta.Protocol):
    def __call__(self, fn: ta.Callable[P, T], *args: P.args, **kwargs: P.kwargs) -> ta.Awaitable[T]: ...


class _RunnerStopIteration(lang.Marker):
    pass


##


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

    def query(self, query: Query) -> ta.AsyncContextManager[AsyncRows]:  # ta.Raises[QueryError]
        @contextlib.asynccontextmanager
        async def inner():
            cm = await self._runner(self._txn.query, query)
            rows = await self._runner(cm.__enter__)
            try:
                yield SyncToAsyncRows(self._runner, rows)
            except BaseException as e:  # noqa
                await self._runner(cm.__exit__, *sys.exc_info())
                raise
            else:
                await self._runner(cm.__exit__, None, None, None)

        return inner()


class SyncToAsyncConn(AsyncConn):
    def __init__(self, runner: Runner, conn: Conn) -> None:
        super().__init__()

        self._runner = runner
        self._conn = conn

    @property
    def adapter(self) -> Adapter:
        return self._conn.adapter

    def begin(self) -> ta.AsyncContextManager[AsyncTransaction]:
        @contextlib.asynccontextmanager
        async def inner():
            cm = await self._runner(self._conn.begin)
            txn = await self._runner(cm.__enter__)
            try:
                yield SyncToAsyncTransaction(self._runner, txn)
            except BaseException as e:  # noqa
                await self._runner(cm.__exit__, *sys.exc_info())
                raise
            else:
                await self._runner(cm.__exit__, None, None, None)

        return inner()

    def query(self, query: Query) -> ta.AsyncContextManager[AsyncRows]:  # ta.Raises[QueryError]
        @contextlib.asynccontextmanager
        async def inner():
            cm = await self._runner(self._conn.query, query)
            rows = await self._runner(cm.__enter__)
            try:
                yield SyncToAsyncRows(self._runner, rows)
            except BaseException as e:  # noqa
                await self._runner(cm.__exit__, *sys.exc_info())
                raise
            else:
                await self._runner(cm.__exit__, None, None, None)

        return inner()


class SyncToAsyncDb(AsyncDb):
    def __init__(self, runner: Runner, db: Db) -> None:
        super().__init__()

        self._runner = runner
        self._db = db

    @property
    def adapter(self) -> Adapter:
        return self._db.adapter

    def connect(self) -> ta.AsyncContextManager[AsyncConn]:
        @contextlib.asynccontextmanager
        async def inner():
            cm = await self._runner(self._db.connect)
            conn = await self._runner(cm.__enter__)
            try:
                yield SyncToAsyncConn(self._runner, conn)
            except BaseException as e:  # noqa
                await self._runner(cm.__exit__, *sys.exc_info())
                raise
            else:
                await self._runner(cm.__exit__, None, None, None)

        return inner()

    def query(self, query: Query) -> ta.AsyncContextManager[AsyncRows]:  # ta.Raises[QueryError]
        @contextlib.asynccontextmanager
        async def inner():
            cm = await self._runner(self._db.connect)
            conn = await self._runner(cm.__enter__)
            try:
                cm2 = await self._runner(conn.query, query)
                rows = await self._runner(cm2.__enter__)
                try:
                    yield SyncToAsyncRows(self._runner, rows)
                except BaseException as e:  # noqa
                    await self._runner(cm2.__exit__, *sys.exc_info())
                    raise
                else:
                    await self._runner(cm2.__exit__, None, None, None)
            except BaseException as e:  # noqa
                await self._runner(cm.__exit__, *sys.exc_info())
                raise
            else:
                await self._runner(cm.__exit__, None, None, None)

        return inner()
