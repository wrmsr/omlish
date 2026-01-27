# @omlish-lite
import abc
import typing as ta

from omlish.lite.abstract import Abstract

from .base import AsyncliteApi
from .base import AsyncliteObject


T = ta.TypeVar('T')


##


class AsyncliteQueue(AsyncliteObject, Abstract, ta.Generic[T]):
    @abc.abstractmethod
    def qsize(self) -> int:
        raise NotImplementedError

    @abc.abstractmethod
    def empty(self) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    def full(self) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    def put(self, item: T, *, timeout: float | None = None) -> ta.Awaitable[None]:
        raise NotImplementedError

    @abc.abstractmethod
    def put_nowait(self, item: T) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def get(self, *, timeout: float | None = None) -> ta.Awaitable[T]:
        raise NotImplementedError

    @abc.abstractmethod
    def get_nowait(self) -> T:
        raise NotImplementedError


class AsyncliteQueues(AsyncliteApi, Abstract):
    @abc.abstractmethod
    def make_queue(self, maxsize: int = 0) -> AsyncliteQueue:
        raise NotImplementedError
