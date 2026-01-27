# @omlish-lite
from ..semaphores import AsyncliteSemaphore
from ..semaphores import AsyncliteSemaphores
from .base import SyncAsyncliteObject
from .base import SyncAsyncliteApi


##


class SyncAsyncliteSemaphore(AsyncliteSemaphore, SyncAsyncliteObject):
    pass


class SyncAsyncliteSemaphores(AsyncliteSemaphores, SyncAsyncliteApi):
    def make_semaphore(self) -> AsyncliteSemaphore:
        raise NotImplementedError
