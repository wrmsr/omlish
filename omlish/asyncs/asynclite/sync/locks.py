# ruff: noqa: UP045
# @omlish-lite
import threading
import typing as ta

from ..locks import AsyncliteLock
from ..locks import AsyncliteLocks
from .base import SyncAsyncliteApi
from .base import SyncAsyncliteObject


##


class SyncAsyncliteLock(AsyncliteLock, SyncAsyncliteObject):
    def __init__(self, u: threading.Lock) -> None:
        super().__init__()

        self._u = u

    async def acquire(self, *, timeout: ta.Optional[float] = None) -> None:
        if timeout is not None and timeout > 0:
            a = self._u.acquire(blocking=False, timeout=timeout)
        else:
            a = self._u.acquire(blocking=True)

        if not a:
            raise TimeoutError

    def acquire_nowait(self) -> bool:
        return self._u.acquire(blocking=False)

    def release(self) -> None:
        self._u.release()

    def locked(self) -> bool:
        return self._u.locked()


class SyncAsyncliteLocks(AsyncliteLocks, SyncAsyncliteApi):
    def make_lock(self) -> AsyncliteLock:
        return SyncAsyncliteLock(threading.Lock())
