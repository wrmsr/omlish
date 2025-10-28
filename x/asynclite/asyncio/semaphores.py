# @omlish-lite
from ..semaphores import AsyncliteSemaphore
from ..semaphores import AsyncliteSemaphores
from .base import AsyncioAsyncliteObject
from .base import AsyncioAsyncliteObjects


##


class AsyncioAsyncliteSemaphore(AsyncliteSemaphore, AsyncioAsyncliteObject):
    pass


class AsyncioAsyncliteSemaphores(AsyncliteSemaphores, AsyncioAsyncliteObjects):
    def make_semaphore(self) -> AsyncliteSemaphore:
        raise NotImplementedError
