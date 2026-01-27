# ruff: noqa: UP045
# @omlish-lite
import asyncio
import typing as ta

from ..events import AsyncliteEvent
from ..events import AsyncliteEvents
from .base import AsyncioAsyncliteApi
from .base import AsyncioAsyncliteObject


##


class AsyncioAsyncliteEvent(AsyncliteEvent, AsyncioAsyncliteObject):
    def __init__(self, u: asyncio.Event) -> None:
        super().__init__()

        self._u = u

    def set(self) -> None:
        return self._u.set()

    def is_set(self) -> bool:
        return self._u.is_set()

    async def wait(self, *, timeout: ta.Optional[float] = None) -> None:
        await self._wait_for(self._u.wait(), timeout=timeout)


class AsyncioAsyncliteEvents(AsyncliteEvents, AsyncioAsyncliteApi):
    def make_event(self) -> AsyncliteEvent:
        return AsyncioAsyncliteEvent(asyncio.Event())
