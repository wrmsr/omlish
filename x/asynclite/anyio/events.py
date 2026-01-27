import typing as ta

import anyio

from ..events import AsyncliteEvent
from ..events import AsyncliteEvents
from .base import AnyioAsyncliteObject
from .base import AnyioAsyncliteApi


##


class AnyioAsyncliteEvent(AsyncliteEvent, AnyioAsyncliteObject):
    def __init__(self, u: anyio.Event) -> None:
        super().__init__()

        self._u = u

    def set(self) -> None:
        return self._u.set()

    def is_set(self) -> bool:
        return self._u.is_set()

    def wait(self, *, timeout: float | None = None) -> ta.Awaitable[None]:
        return self._u.wait()


class AnyioAsyncliteEvents(AsyncliteEvents, AnyioAsyncliteApi):
    def make_event(self) -> AsyncliteEvent:
        return AnyioAsyncliteEvent(anyio.Event())
