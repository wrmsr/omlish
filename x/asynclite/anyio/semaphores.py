from ..semaphores import AsyncliteSemaphore
from ..semaphores import AsyncliteSemaphores
from .base import AnyioAsyncliteObject
from .base import AnyioAsyncliteApi


##


class AnyioAsyncliteSemaphore(AsyncliteSemaphore, AnyioAsyncliteObject):
    pass


class AnyioAsyncliteSemaphores(AsyncliteSemaphores, AnyioAsyncliteApi):
    def make_semaphore(self) -> AsyncliteSemaphore:
        raise NotImplementedError

