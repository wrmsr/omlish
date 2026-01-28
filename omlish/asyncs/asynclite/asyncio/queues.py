# ruff: noqa: UP045
# @omlish-lite
import asyncio
import typing as ta

from ..queues import AsyncliteQueue
from ..queues import AsyncliteQueues
from .base import AsyncioAsyncliteApi
from .base import AsyncioAsyncliteObject


T = ta.TypeVar('T')


##


class AsyncioAsyncliteQueue(AsyncliteQueue[T], AsyncioAsyncliteObject):
    def __init__(self, u: 'asyncio.Queue[T]') -> None:
        super().__init__()

        self._u = u

    async def aclose(self) -> None:
        pass

    def qsize(self) -> int:
        return self._u.qsize()

    def empty(self) -> bool:
        return self._u.empty()

    def full(self) -> bool:
        return self._u.full()

    async def put(self, item: T, *, timeout: ta.Optional[float] = None) -> None:
        await self._wait_for(self._u.put(item), timeout=timeout)

    def put_nowait(self, item: T) -> None:
        with self._translate_exceptions():
            self._u.put_nowait(item)

    async def get(self, *, timeout: ta.Optional[float] = None) -> T:
        return await self._wait_for(self._u.get(), timeout=timeout)

    def get_nowait(self) -> T:
        with self._translate_exceptions():
            return self._u.get_nowait()


class AsyncioAsyncliteQueues(AsyncliteQueues, AsyncioAsyncliteApi):
    def make_queue(self, maxsize: int = 0) -> AsyncliteQueue:
        return AsyncioAsyncliteQueue(asyncio.Queue(maxsize))
