import contextlib
import typing as ta

import sqlalchemy as sa
import sqlalchemy.ext.asyncio as saa

from .. import asyncs as au


T = ta.TypeVar('T')
P = ta.ParamSpec('P')


AsyncEngineLike = ta.Union[saa.AsyncEngine, 'AsyncEngineAdapter']
AsyncConnectionLike = ta.Union[saa.AsyncConnection, 'AsyncConnectionAdapter']
AsyncTransactionLike = ta.Union[saa.AsyncTransaction, 'AsyncTransactionAdapter']


class AsyncTransactionAdapter:
    def __init__(self, underlying: saa.AsyncTransaction) -> None:
        super().__init__()
        self._underlying = underlying

    @property
    def underlying(self) -> saa.AsyncTransaction:
        return self._underlying

    ##

    @au.mark_asyncio
    async def close(self) -> None:
        await au.from_asyncio(self._underlying.close)()

    @au.mark_asyncio
    async def rollback(self) -> None:
        await au.from_asyncio(self._underlying.rollback)()

    @au.mark_asyncio
    async def commit(self) -> None:
        await au.from_asyncio(self._underlying.commit)()


class AsyncConnectionAdapter:
    def __init__(self, underlying: saa.AsyncConnection) -> None:
        super().__init__()
        self._underlying = underlying

    @property
    def underlying(self) -> saa.AsyncConnection:
        return self._underlying

    ##

    @contextlib.asynccontextmanager
    @au.mark_asyncio
    async def begin(self) -> ta.Generator[AsyncTransactionAdapter, None, None]:
        async with au.from_asyncio_context(self._underlying.begin()) as u:
            yield AsyncTransactionAdapter(u)

    @au.mark_asyncio
    async def execute(
            self,
            statement: ta.Any,
            *args: ta.Any,
            **kwargs: ta.Any,
    ) -> sa.CursorResult[ta.Any]:
        return await au.from_asyncio(self._underlying.execute)(statement, *args, **kwargs)

    @au.mark_asyncio
    async def run_sync(
            self,
            fn: ta.Callable[ta.Concatenate[sa.Connection, P], T],
            *args: P.args,
            **kwargs: P.kwargs,
    ) -> T:
        return await au.from_asyncio(self._underlying.run_sync)(fn, *args, **kwargs)


class AsyncEngineAdapter:
    def __init__(self, underlying: saa.AsyncEngine) -> None:
        super().__init__()
        self._underlying = underlying

    @property
    def underlying(self) -> saa.AsyncEngine:
        return self._underlying

    ##

    @contextlib.asynccontextmanager
    @au.mark_asyncio
    async def connect(self) -> ta.AsyncContextManager[AsyncConnectionAdapter]:
        async with au.from_asyncio_context(self._underlying.connect()) as u:
            yield AsyncConnectionAdapter(u)

    @au.mark_asyncio
    async def dispose(self, close: bool = True) -> None:
        await au.from_asyncio(self._underlying.dispose)(close)


##


@ta.overload
def async_adapt(obj: AsyncEngineAdapter) -> AsyncEngineAdapter:
    ...


@ta.overload
def async_adapt(obj: AsyncConnectionAdapter) -> AsyncConnectionAdapter:
    ...


@ta.overload
def async_adapt(obj: AsyncTransactionAdapter) -> AsyncTransactionAdapter:
    ...


@ta.overload
def async_adapt(obj: saa.AsyncEngine) -> AsyncEngineAdapter:
    ...


@ta.overload
def async_adapt(obj: saa.AsyncConnection) -> AsyncConnectionAdapter:
    ...


@ta.overload
def async_adapt(obj: saa.AsyncTransaction) -> AsyncTransactionAdapter:
    ...


def async_adapt(obj: ta.Any) -> ta.Any:
    if isinstance(obj, (AsyncEngineAdapter, AsyncConnectionAdapter, AsyncTransactionAdapter)):
        return obj
    if isinstance(obj, saa.AsyncTransaction):
        return AsyncTransactionAdapter(obj)
    if isinstance(obj, saa.AsyncConnection):
        return AsyncConnectionAdapter(obj)
    if isinstance(obj, saa.AsyncEngine):
        return AsyncEngineAdapter(obj)
    raise TypeError(obj)
