"""
TODO:
 - Maysync impls?
 - base Protocol so adapters and real sa impls can be used interchangeably (if in asyncio ctx)?
"""
import contextlib
import typing as ta

import sqlalchemy as sa
import sqlalchemy.ext.asyncio as saa

from ...asyncs import all as au


T = ta.TypeVar('T')
P = ta.ParamSpec('P')


AsyncEngineLike = ta.Union[saa.AsyncEngine, 'AsyncEngine']
AsyncConnectionLike = ta.Union[saa.AsyncConnection, 'AsyncConnection']
AsyncTransactionLike = ta.Union[saa.AsyncTransaction, 'AsyncTransaction']


class AsyncTransaction:
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


class AsyncConnection:
    def __init__(self, underlying: saa.AsyncConnection) -> None:
        super().__init__()
        self._underlying = underlying

    @property
    def underlying(self) -> saa.AsyncConnection:
        return self._underlying

    ##

    @contextlib.asynccontextmanager
    @au.mark_asyncio
    async def begin(self) -> ta.AsyncIterator[AsyncTransaction]:
        async with au.from_asyncio_context(self._underlying.begin()) as u:
            yield AsyncTransaction(u)

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


class AsyncEngine:
    def __init__(self, underlying: saa.AsyncEngine) -> None:
        super().__init__()
        self._underlying = underlying

    @property
    def underlying(self) -> saa.AsyncEngine:
        return self._underlying

    ##

    @contextlib.asynccontextmanager
    @au.mark_asyncio
    async def connect(self) -> ta.AsyncIterator[AsyncConnection]:
        async with au.from_asyncio_context(self._underlying.connect()) as u:
            yield AsyncConnection(u)

    @au.mark_asyncio
    async def dispose(self, close: bool = True) -> None:
        await au.from_asyncio(self._underlying.dispose)(close)


##


@ta.overload
def async_adapt(obj: AsyncEngine) -> AsyncEngine:
    ...


@ta.overload
def async_adapt(obj: AsyncConnection) -> AsyncConnection:
    ...


@ta.overload
def async_adapt(obj: AsyncTransaction) -> AsyncTransaction:
    ...


@ta.overload
def async_adapt(obj: saa.AsyncEngine) -> AsyncEngine:
    ...


@ta.overload
def async_adapt(obj: saa.AsyncConnection) -> AsyncConnection:
    ...


@ta.overload
def async_adapt(obj: saa.AsyncTransaction) -> AsyncTransaction:
    ...


def async_adapt(obj: ta.Any) -> ta.Any:
    if isinstance(obj, (AsyncEngine, AsyncConnection, AsyncTransaction)):
        return obj
    if isinstance(obj, saa.AsyncTransaction):
        return AsyncTransaction(obj)
    if isinstance(obj, saa.AsyncConnection):
        return AsyncConnection(obj)
    if isinstance(obj, saa.AsyncEngine):
        return AsyncEngine(obj)
    raise TypeError(obj)
