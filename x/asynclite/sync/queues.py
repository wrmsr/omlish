# @omlish-lite
import queue
import typing as ta

from ..queues import AsyncliteQueue
from ..queues import AsyncliteQueues
from .base import SyncAsyncliteObject
from .base import SyncAsyncliteApi


T = ta.TypeVar('T')


##


class SyncAsyncliteQueue(AsyncliteQueue[T], SyncAsyncliteObject):
    def __init__(self, u: queue.Queue[T]) -> None:
        super().__init__()

        self._u = u

    def qsize(self) -> int:
        return self._u.qsize()

    def empty(self) -> bool:
        return self._u.empty()

    def full(self) -> bool:
        return self._u.full()

    async def put(self, item: T, *, timeout: float | None = None) -> None:
        with self._translate_exceptions():
            self._u.put(item, block=True, timeout=timeout)

    def put_nowait(self, item: T) -> None:
        with self._translate_exceptions():
            self._u.put_nowait(item)

    async def get(self, *, timeout: float | None = None) -> T:
        with self._translate_exceptions():
            return self._u.get(block=True, timeout=timeout)

    def get_nowait(self) -> T:
        with self._translate_exceptions():
            return self._u.get_nowait()


class SyncAsyncliteQueues(AsyncliteQueues, SyncAsyncliteApi):
    def make_queue(self, maxsize: int = 0) -> AsyncliteQueue:
        return SyncAsyncliteQueue(queue.Queue(maxsize))
