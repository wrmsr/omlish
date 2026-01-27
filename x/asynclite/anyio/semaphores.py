import anyio

from ..semaphores import AsyncliteSemaphore
from ..semaphores import AsyncliteSemaphores
from .base import AnyioAsyncliteObject
from .base import AnyioAsyncliteApi


##


class AnyioAsyncliteSemaphore(AsyncliteSemaphore, AnyioAsyncliteObject):
    def __init__(self, u: anyio.Semaphore) -> None:
        super().__init__()

        self._u = u

    async def acquire(self, *, timeout: float | None = None) -> None:
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


class AnyioAsyncliteSemaphores(AsyncliteSemaphores, AnyioAsyncliteApi):
    def make_semaphore(self, value: int = 1) -> AsyncliteSemaphore:
        return AnyioAsyncliteSemaphore(anyio.Semaphore(value))

