# @omlish-lite
import asyncio

from ..events import AsyncliteEvent
from ..events import AsyncliteEvents
from .base import AsyncioAsyncliteObject
from .base import AsyncioAsyncliteObjects


##


class AsyncioAsyncliteEvent(AsyncliteEvent, AsyncioAsyncliteObject):
    def __init__(self, u: asyncio.Event) -> None:
        super().__init__()

        self._u = u

    def set(self) -> None:
        return self._u.set()

    def is_set(self) -> bool:
        return self._u.is_set()

    async def wait(self, *, timeout: float | None = None) -> None:
        await self._wait_for(self._u.wait(), timeout=timeout)


class AsyncioAsyncliteEvents(AsyncliteEvents, AsyncioAsyncliteObjects):
    def make_event(self) -> AsyncliteEvent:
        return AsyncioAsyncliteEvent(asyncio.Event())
