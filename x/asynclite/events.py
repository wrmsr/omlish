# @omlish-lite
import abc
import typing as ta

from omlish.lite.abstract import Abstract

from .base import AsyncliteObject
from .base import AsyncliteApi


##


class AsyncliteEvent(AsyncliteObject, Abstract):
    @abc.abstractmethod
    def set(self) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def is_set(self) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    def wait(self, *, timeout: float | None = None) -> ta.Awaitable[None]:
        raise NotImplementedError


class AsyncliteEvents(AsyncliteApi, Abstract):
    @abc.abstractmethod
    def make_event(self) -> AsyncliteEvent:
        raise NotImplementedError
