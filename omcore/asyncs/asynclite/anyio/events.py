# ruff: noqa: UP045
import typing as ta

import anyio

from ..events import AsyncliteEvent
from ..events import AsyncliteEvents
from .base import AnyioAsyncliteApi
from .base import AnyioAsyncliteObject


##


class AnyioAsyncliteEvent(AsyncliteEvent, AnyioAsyncliteObject):
    def __init__(self, u: anyio.Event) -> None:
        super().__init__()

        self._u = u

    def set(self) -> None:
        return self._u.set()

    def is_set(self) -> bool:
        return self._u.is_set()

    async def wait(self, *, timeout: ta.Optional[float] = None) -> None:
        if timeout is not None:
            with anyio.fail_after(timeout):
                await self._u.wait()

        else:
            await self._u.wait()


class AnyioAsyncliteEvents(AsyncliteEvents, AnyioAsyncliteApi):
    def make_event(self) -> AsyncliteEvent:
        return AnyioAsyncliteEvent(anyio.Event())
