from ..queues import AsyncliteQueue
from ..queues import AsyncliteQueues
from .base import AnyioAsyncliteObject
from .base import AnyioAsyncliteApi


##


class AnyioAsyncliteQueue(AsyncliteQueue, AnyioAsyncliteObject):
    pass


class AnyioAsyncliteQueues(AsyncliteQueues, AnyioAsyncliteApi):
    def make_queue(self) -> AsyncliteQueue:
        raise NotImplementedError
