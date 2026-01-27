# @omlish-lite
import abc

from omlish.lite.abstract import Abstract

from .base import AsyncliteObject
from .base import AsyncliteApi


##


class AsyncliteQueue(AsyncliteObject, Abstract):
    pass


class AsyncliteQueues(AsyncliteApi, Abstract):
    @abc.abstractmethod
    def make_queue(self) -> AsyncliteQueue:
        raise NotImplementedError
