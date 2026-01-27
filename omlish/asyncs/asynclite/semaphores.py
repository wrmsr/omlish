# ruff: noqa: UP006 UP045
# @omlish-lite
import abc
import types
import typing as ta

from ...lite.abstract import Abstract
from .base import AsyncliteApi
from .base import AsyncliteObject


##


class AsyncliteSemaphore(AsyncliteObject, Abstract):
    async def __aenter__(self) -> None:
        await self.acquire()

    async def __aexit__(
            self,
            exc_type: ta.Optional[ta.Type[BaseException]] = None,
            exc_val: ta.Optional[BaseException] = None,
            exc_tb: ta.Optional[types.TracebackType] = None,
    ) -> None:
        self.release()

    @abc.abstractmethod
    def acquire(self, *, timeout: ta.Optional[float] = None) -> ta.Awaitable[None]:
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
