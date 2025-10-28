# @omlish-lite
import abc

from omlish.lite.abstract import Abstract

from .base import AsyncliteObject
from .base import AsyncliteObjects


##


class AsyncliteQueue(AsyncliteObject, Abstract):
    pass


class AsyncliteQueues(AsyncliteObjects, Abstract):
    @abc.abstractmethod
    def make_queue(self) -> AsyncliteQueue:
        raise NotImplementedError
