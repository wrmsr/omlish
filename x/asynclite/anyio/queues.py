from ..queues import AsyncliteQueue
from ..queues import AsyncliteQueues
from .base import AnyioAsyncliteObject
from .base import AnyioAsyncliteObjects


##


class AnyioAsyncliteQueue(AsyncliteQueue, AnyioAsyncliteObject):
    pass


class AnyioAsyncliteQueues(AsyncliteQueues, AnyioAsyncliteObjects):
    def make_queue(self) -> AsyncliteQueue:
        raise NotImplementedError
