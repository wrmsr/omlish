# @omlish-lite
import asyncio

from ..locks import AsyncliteLock
from ..locks import AsyncliteLocks
from .base import AsyncioAsyncliteObject
from .base import AsyncioAsyncliteObjects


##


class AsyncioAsyncliteLock(AsyncliteLock, AsyncioAsyncliteObject):
    def __init__(self, u: asyncio.Lock) -> None:
        super().__init__()

        self._u = u

    async def acquire(self, *, timeout: float | None = None) -> None:
        await self._wait_for(self._u.acquire(), timeout=timeout)

    def release(self) -> None:
        self._u.release()

    def locked(self) -> bool:
        return self._u.locked()


class AsyncioAsyncliteLocks(AsyncliteLocks, AsyncioAsyncliteObjects):
    def make_lock(self) -> AsyncliteLock:
        return AsyncioAsyncliteLock(asyncio.Lock())
