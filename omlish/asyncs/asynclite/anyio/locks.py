# ruff: noqa: UP045
import typing as ta

import anyio

from ..locks import AsyncliteLock
from ..locks import AsyncliteLocks
from .base import AnyioAsyncliteApi
from .base import AnyioAsyncliteObject


##


class AnyioAsyncliteLock(AsyncliteLock, AnyioAsyncliteObject):
    def __init__(self, u: anyio.Lock) -> None:
        super().__init__()

        self._u = u

    async def acquire(self, *, timeout: ta.Optional[float] = None) -> None:
        if timeout is not None:
            with anyio.fail_after(timeout):
                await self._u.acquire()

        else:
            await self._u.acquire()

    def acquire_nowait(self) -> bool:
        try:
            self._u.acquire_nowait()
            return True

        except anyio.WouldBlock:
            return False

    def release(self) -> None:
        self._u.release()

    def locked(self) -> bool:
        return self._u.locked()


class AnyioAsyncliteLocks(AsyncliteLocks, AnyioAsyncliteApi):
    def make_lock(self) -> AsyncliteLock:
        return AnyioAsyncliteLock(anyio.Lock())
