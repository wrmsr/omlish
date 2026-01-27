# @omlish-lite
import abc

from omlish.lite.abstract import Abstract

from .base import AsyncliteObject
from .base import AsyncliteApi


##


class AsyncliteSemaphore(AsyncliteObject, Abstract):
    pass


class AsyncliteSemaphores(AsyncliteApi, Abstract):
    @abc.abstractmethod
    def make_semaphore(self) -> AsyncliteSemaphore:
        raise NotImplementedError
