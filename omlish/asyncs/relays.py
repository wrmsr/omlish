# @omlish-lite
import abc
import typing as ta

from ..lite.abstract import Abstract
from ..sync.relays import BufferRelay


T = ta.TypeVar('T')


##


class AsyncBufferRelay(Abstract, ta.Generic[T]):
    @abc.abstractmethod
    def push(self, *vs: T) -> ta.Awaitable[None]:
        raise NotImplementedError

    @abc.abstractmethod
    def swap(self) -> ta.Awaitable[ta.Sequence[T]]:
        raise NotImplementedError


##


class SchedulingAsyncBufferRelay(AsyncBufferRelay[T]):
    def __init__(
            self,
            schedule_fn: ta.Callable[[], ta.Awaitable[None]],
    ) -> None:
        super().__init__()

        self._schedule_fn = schedule_fn

    async def push(self, *vs: T) -> None:
        raise NotImplementedError

    async def swap(self) -> ta.Sequence[T]:
        raise NotImplementedError


##


class SyncToAsyncBufferRelay(BufferRelay[T], Abstract, ta.Generic[T]):
    @abc.abstractmethod
    async def wait(self) -> None:
        raise NotImplementedError
