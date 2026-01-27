# ruff: noqa: UP045
# @omlish-lite
import abc
import typing as ta

from ...lite.abstract import Abstract
from .base import AsyncliteApi
from .base import AsyncliteObject


##


class AsyncliteEvent(AsyncliteObject, Abstract):
    @abc.abstractmethod
    def set(self) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def is_set(self) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    def wait(self, *, timeout: ta.Optional[float] = None) -> ta.Awaitable[None]:
        raise NotImplementedError


class AsyncliteEvents(AsyncliteApi, Abstract):
    @abc.abstractmethod
    def make_event(self) -> AsyncliteEvent:
        raise NotImplementedError
