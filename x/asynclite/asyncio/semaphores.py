# @omlish-lite
from ..semaphores import AsyncliteSemaphore
from ..semaphores import AsyncliteSemaphores
from .base import AsyncioAsyncliteObject
from .base import AsyncioAsyncliteApi


##


class AsyncioAsyncliteSemaphore(AsyncliteSemaphore, AsyncioAsyncliteObject):
    pass


class AsyncioAsyncliteSemaphores(AsyncliteSemaphores, AsyncioAsyncliteApi):
    def make_semaphore(self) -> AsyncliteSemaphore:
        raise NotImplementedError
