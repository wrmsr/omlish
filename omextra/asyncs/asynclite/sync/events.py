# @omlish-lite
import threading

from ..events import AsyncliteEvent
from ..events import AsyncliteEvents
from .base import SyncAsyncliteApi
from .base import SyncAsyncliteObject


##


class SyncAsyncliteEvent(AsyncliteEvent, SyncAsyncliteObject):
    def __init__(self, u: threading.Event) -> None:
        super().__init__()

        self._u = u

    def set(self) -> None:
        return self._u.set()

    def is_set(self) -> bool:
        return self._u.is_set()

    async def wait(self, *, timeout: float | None = None) -> None:
        if not self._u.wait(timeout=timeout):
            raise TimeoutError


class SyncAsyncliteEvents(AsyncliteEvents, SyncAsyncliteApi):
    def make_event(self) -> AsyncliteEvent:
        return SyncAsyncliteEvent(threading.Event())
