# ruff: noqa: UP045
# @omlish-lite
import queue
import typing as ta

from ..queues import AsyncliteQueue
from ..queues import AsyncliteQueues
from .base import SyncAsyncliteApi
from .base import SyncAsyncliteObject


T = ta.TypeVar('T')


##


class SyncAsyncliteQueue(AsyncliteQueue[T], SyncAsyncliteObject):
    def __init__(self, u: 'queue.Queue[T]') -> None:
        super().__init__()

        self._u = u

    async def aclose(self) -> None:
        pass

    def qsize(self) -> int:
        return self._u.qsize()

    def empty(self) -> bool:
        return self._u.empty()

    def full(self) -> bool:
        return self._u.full()

    async def put(self, item: T, *, timeout: ta.Optional[float] = None) -> None:
        self._u.put(item, block=True, timeout=timeout)

    def put_nowait(self, item: T) -> None:
        self._u.put_nowait(item)

    async def get(self, *, timeout: ta.Optional[float] = None) -> T:
        return self._u.get(block=True, timeout=timeout)

    def get_nowait(self) -> T:
        return self._u.get_nowait()


class SyncAsyncliteQueues(AsyncliteQueues, SyncAsyncliteApi):
    def make_queue(self, maxsize: int = 0) -> AsyncliteQueue:
        return SyncAsyncliteQueue(queue.Queue(maxsize))
