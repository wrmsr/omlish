# @omlish-lite
import abc
import types
import typing as ta

from omlish.lite.abstract import Abstract

from .base import AsyncliteObject
from .base import AsyncliteApi


##


class AsyncliteSemaphore(AsyncliteObject, Abstract):
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


class AsyncliteSemaphores(AsyncliteApi, Abstract):
    @abc.abstractmethod
    def make_semaphore(self, value: int = 1) -> AsyncliteSemaphore:
        raise NotImplementedError
