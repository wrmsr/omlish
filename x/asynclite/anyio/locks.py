import typing as ta

import anyio

from ..locks import AsyncliteLock
from ..locks import AsyncliteLocks
from .base import AnyioAsyncliteObject
from .base import AnyioAsyncliteApi


##


class AnyioAsyncliteLock(AsyncliteLock, AnyioAsyncliteObject):
    def __init__(self, u: anyio.Lock) -> None:
        super().__init__()

        self._u = u

    def acquire(self, *, timeout: float | None = None) -> ta.Awaitable[None]:
        if timeout is not None and timeout:
            return self._u.acquire()

        raise NotImplementedError

    def release(self) -> None:
        self._u.release()

    def locked(self) -> bool:
        return self._u.locked()


class AnyioAsyncliteLocks(AsyncliteLocks, AnyioAsyncliteApi):
    def make_lock(self) -> AsyncliteLock:
        return AnyioAsyncliteLock(anyio.Lock())
