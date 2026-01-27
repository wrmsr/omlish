# ruff: noqa: UP045
# @omlish-lite
import threading
import typing as ta

from ..semaphores import AsyncliteSemaphore
from ..semaphores import AsyncliteSemaphores
from .base import SyncAsyncliteApi
from .base import SyncAsyncliteObject


##


class SyncAsyncliteSemaphore(AsyncliteSemaphore, SyncAsyncliteObject):
    def __init__(self, u: threading.Semaphore) -> None:
        super().__init__()

        self._u = u

    async def acquire(self, *, timeout: ta.Optional[float] = None) -> None:
        if not self._u.acquire(blocking=True, timeout=timeout):
            raise TimeoutError

    def acquire_nowait(self) -> bool:
        return self._u.acquire(blocking=False)

    def release(self) -> None:
        self._u.release()


class SyncAsyncliteSemaphores(AsyncliteSemaphores, SyncAsyncliteApi):
    def make_semaphore(self, value: int = 1) -> AsyncliteSemaphore:
        return SyncAsyncliteSemaphore(threading.Semaphore(value))
