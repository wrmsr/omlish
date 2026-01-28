# ruff: noqa: UP045
# @omlish-lite
import abc
import typing as ta

from ...lite.abstract import Abstract
from .base import AsyncliteApi
from .base import AsyncliteCloseable
from .base import AsyncliteObject


T = ta.TypeVar('T')


##


class AsyncliteQueue(AsyncliteCloseable, AsyncliteObject, Abstract, ta.Generic[T]):
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
    def put(self, item: T, *, timeout: ta.Optional[float] = None) -> ta.Awaitable[None]:
        raise NotImplementedError

    @abc.abstractmethod
    def put_nowait(self, item: T) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def get(self, *, timeout: ta.Optional[float] = None) -> ta.Awaitable[T]:
        raise NotImplementedError

    @abc.abstractmethod
    def get_nowait(self) -> T:
        raise NotImplementedError


class AsyncliteQueues(AsyncliteApi, Abstract):
    @abc.abstractmethod
    def make_queue(self, maxsize: int = 0) -> AsyncliteQueue:
        raise NotImplementedError
