# @omlish-lite
import abc
import types
import typing as ta

from omlish.lite.abstract import Abstract

from .base import AsyncliteApi
from .base import AsyncliteObject


##


class AsyncliteLock(AsyncliteObject, Abstract):
    """Non-reentrant."""

    async def __aenter__(self) -> None:
        await self.acquire()

    async def __aexit__(
            self,
            exc_type: type[BaseException] | None = None,
            exc_val: BaseException | None = None,
            exc_tb: types.TracebackType | None = None,
    ) -> None:
        self.release()

    @abc.abstractmethod
    def acquire(self, *, timeout: float | None = None) -> ta.Awaitable[None]:
        raise NotImplementedError

    @abc.abstractmethod
    def acquire_nowait(self) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    def release(self) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def locked(self) -> bool:
        raise NotImplementedError


class AsyncliteLocks(AsyncliteApi, Abstract):
    @abc.abstractmethod
    def make_lock(self) -> AsyncliteLock:
        raise NotImplementedError
