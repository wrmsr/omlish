# ruff: noqa: UP045
# @omlish-lite
import asyncio
import typing as ta

from ..semaphores import AsyncliteSemaphore
from ..semaphores import AsyncliteSemaphores
from .base import AsyncioAsyncliteApi
from .base import AsyncioAsyncliteObject


##


class AsyncioAsyncliteSemaphore(AsyncliteSemaphore, AsyncioAsyncliteObject):
    def __init__(self, u: asyncio.Semaphore) -> None:
        super().__init__()

        self._u = u

    async def acquire(self, *, timeout: ta.Optional[float] = None) -> None:
        await self._wait_for(self._u.acquire(), timeout=timeout)

    def acquire_nowait(self) -> bool:
        # asyncio.Semaphore doesn't have acquire_nowait, so we check if we can acquire
        if self._u.locked():
            return False

        # Manually decrement the internal counter
        self._u._value -= 1  # noqa
        return True

    def release(self) -> None:
        self._u.release()


class AsyncioAsyncliteSemaphores(AsyncliteSemaphores, AsyncioAsyncliteApi):
    def make_semaphore(self, value: int = 1) -> AsyncliteSemaphore:
        return AsyncioAsyncliteSemaphore(asyncio.Semaphore(value))
