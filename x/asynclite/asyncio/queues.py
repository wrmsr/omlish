# @omlish-lite
from ..queues import AsyncliteQueue
from ..queues import AsyncliteQueues
from .base import AsyncioAsyncliteObject
from .base import AsyncioAsyncliteApi


##


class AsyncioAsyncliteQueue(AsyncliteQueue, AsyncioAsyncliteObject):
    pass


class AsyncioAsyncliteQueues(AsyncliteQueues, AsyncioAsyncliteApi):
    def make_queue(self) -> AsyncliteQueue:
        raise NotImplementedError
