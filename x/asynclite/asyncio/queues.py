# @omlish-lite
from ..queues import AsyncliteQueue
from ..queues import AsyncliteQueues
from .base import AsyncioAsyncliteObject
from .base import AsyncioAsyncliteObjects


##


class AsyncioAsyncliteQueue(AsyncliteQueue, AsyncioAsyncliteObject):
    pass


class AsyncioAsyncliteQueues(AsyncliteQueues, AsyncioAsyncliteObjects):
    def make_queue(self) -> AsyncliteQueue:
        raise NotImplementedError
