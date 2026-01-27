# ruff: noqa: UP045
# @omlish-lite
import asyncio
import typing as ta

from ..locks import AsyncliteLock
from ..locks import AsyncliteLocks
from .base import AsyncioAsyncliteApi
from .base import AsyncioAsyncliteObject


##


class AsyncioAsyncliteLock(AsyncliteLock, AsyncioAsyncliteObject):
    def __init__(self, u: asyncio.Lock) -> None:
        super().__init__()

        self._u = u

    async def acquire(self, *, timeout: ta.Optional[float] = None) -> None:
        with self._translate_exceptions():
            await self._wait_for(self._u.acquire(), timeout=timeout)

    def acquire_nowait(self) -> bool:
        # NOTE: Currently does not mirror 'fair scheduling' logic of asyncio:
        #   `if (not self._locked and (self._waiters is None or all(w.cancelled() for w in self._waiters))):`
        if self._u.locked():
            return False

        # Manually acquire the lock by setting the internal state
        self._u._locked = True  # type: ignore[attr-defined]  # noqa
        return True

    def release(self) -> None:
        self._u.release()

    def locked(self) -> bool:
        return self._u.locked()


class AsyncioAsyncliteLocks(AsyncliteLocks, AsyncioAsyncliteApi):
    def make_lock(self) -> AsyncliteLock:
        return AsyncioAsyncliteLock(asyncio.Lock())
