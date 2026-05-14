# ruff: noqa: RUF013 UP037 UP045
import contextlib
import functools
import typing as ta

from ... import lang
from .adapters import Adapter
from .columns import Columns
from .core import AsyncConn
from .core import AsyncDb
from .core import AsyncRows
from .core import AsyncTxn
from .core import Conn
from .core import Db
from .core import Rows
from .core import Txn
from .queries import Queryable
from .rows import Row


with lang.auto_proxy_import(globals()):
    import asyncio
    import concurrent.futures as cf

    from ...asyncs.asyncio import all as au


T = ta.TypeVar('T')
P = ta.ParamSpec('P')


##


class SyncToAsyncRunner(ta.Protocol):
    def __call__(self, fn: ta.Callable[P, T], *args: P.args, **kwargs: P.kwargs) -> ta.Awaitable[T]: ...


SyncToAsyncRunnerFactory: ta.TypeAlias = ta.Callable[[], ta.AsyncContextManager[SyncToAsyncRunner]]


##


class ImmediateSyncToAsyncRunner:
    async def __aenter__(self) -> ta.Self:
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    async def __call__(self, fn: ta.Callable[P, T], *args: P.args, **kwargs: P.kwargs) -> T:
        return fn(*args, **kwargs)


class AsyncioToExecutorSyncToAsyncRunner:
    def __init__(
            self,
            exe: ta.Optional['cf.Executor'] = None,
            loop: ta.Optional['asyncio.AbstractEventLoop'] = None,
    ) -> None:
        super().__init__()

        self._te = au.ToExecutor(exe, loop)

    @classmethod
    def factory(
            cls,
            exe: ta.Optional['cf.Executor'] = None,
            loop: ta.Optional['asyncio.AbstractEventLoop'] = None,
    ) -> ta.Callable[[], AsyncioToExecutorSyncToAsyncRunner]:
        return functools.partial(cls, exe, loop)

    async def __aenter__(self) -> ta.Self:
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    async def __call__(self, fn: ta.Callable[P, T], *args: P.args, **kwargs: P.kwargs) -> T:
        return await self._te(fn, *args, **kwargs)


##


@ta.final
class _SyncToAsyncRunnerContextManager:
    def __init__(self, runner: SyncToAsyncRunner, fn: ta.Callable, wrapper: ta.Any) -> None:
        self._runner, self._fn, self._wrapper = runner, fn, wrapper

    _cm: ta.Any

    async def __aenter__(self):
        self._cm = await self._runner(self._fn)
        return self._wrapper(self._runner, await self._runner(self._cm.__enter__))

    async def __aexit__(self, et, e, tb):
        return await self._runner(self._cm.__exit__, et, e, tb)


##


class _SyncToAsyncRunnerStopIteration(lang.Marker):
    pass


class SyncToAsyncRows(AsyncRows):
    def __init__(self, runner: SyncToAsyncRunner, rows: Rows) -> None:
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
                return _SyncToAsyncRunnerStopIteration

        if (v := await self._runner(inner)) is _SyncToAsyncRunnerStopIteration:
            raise StopAsyncIteration

        return v


class SyncToAsyncTxn(AsyncTxn):
    def __init__(self, runner: SyncToAsyncRunner, txn: Txn) -> None:
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
        return _SyncToAsyncRunnerContextManager(self._runner, lambda: self._txn.query(query), SyncToAsyncRows)


class SyncToAsyncConn(AsyncConn):
    def __init__(self, runner: SyncToAsyncRunner, conn: Conn) -> None:
        super().__init__()

        self._runner = runner
        self._conn = conn

    @property
    def adapter(self) -> Adapter:
        return self._conn.adapter

    def begin(self) -> ta.AsyncContextManager[AsyncTxn]:
        return _SyncToAsyncRunnerContextManager(self._runner, self._conn.begin, SyncToAsyncTxn)

    def query(self, query: Queryable) -> ta.AsyncContextManager[AsyncRows]:  # ta.Raises[QueryError]
        return _SyncToAsyncRunnerContextManager(self._runner, lambda: self._conn.query(query), SyncToAsyncRows)


class SyncToAsyncDb(AsyncDb):
    def __init__(
            self,
            runner_factory: SyncToAsyncRunnerFactory,
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

        rcm = _SyncToAsyncRunnerContextManager(runner, self._db.connect, SyncToAsyncConn)
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
