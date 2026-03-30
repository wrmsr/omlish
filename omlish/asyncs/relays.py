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

        self._buffer: list[T] = []
        self._has_scheduled: bool = False

    async def push(self, *vs: T) -> None:
        self._buffer.extend(vs)
        if self._buffer and not self._has_scheduled:
            self._has_scheduled = True
            await self._schedule_fn()

    async def swap(self) -> ta.Sequence[T]:
        buf, self._buffer = self._buffer, []
        self._has_scheduled = False
        return buf


##


class SyncToAsyncBufferRelay(BufferRelay[T], Abstract, ta.Generic[T]):
    @abc.abstractmethod
    async def wait(self) -> None:
        raise NotImplementedError
