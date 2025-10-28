from ..semaphores import AsyncliteSemaphore
from ..semaphores import AsyncliteSemaphores
from .base import AnyioAsyncliteObject
from .base import AnyioAsyncliteObjects


##


class AnyioAsyncliteSemaphore(AsyncliteSemaphore, AnyioAsyncliteObject):
    pass


class AnyioAsyncliteSemaphores(AsyncliteSemaphores, AnyioAsyncliteObjects):
    def make_semaphore(self) -> AsyncliteSemaphore:
        raise NotImplementedError

