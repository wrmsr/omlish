# @omlish-lite
import abc
import typing as ta

from ..lite.abstract import Abstract


T = ta.TypeVar('T')


##


class AsyncBufferRelay(Abstract, ta.Generic[T]):
    @abc.abstractmethod
    def push(self, *vs: T) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def swap(self) -> ta.Sequence[T]:
        raise NotImplementedError

    @abc.abstractmethod
    async def wait(self) -> None:
        raise NotImplementedError
