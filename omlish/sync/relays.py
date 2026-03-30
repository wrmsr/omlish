# ruff: noqa: UP006 UP043 UP045
# @omlish-lite
import abc
import threading
import typing as ta

from ..lite.abstract import Abstract


T = ta.TypeVar('T')


##


class BufferRelay(Abstract, ta.Generic[T]):
    @abc.abstractmethod
    def push(self, *vs: T) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def swap(self) -> ta.Sequence[T]:
        raise NotImplementedError


##


class WakingBufferRelay(BufferRelay[T]):
    def __init__(
            self,
            wake_fn: ta.Callable[[], None],
    ) -> None:
        super().__init__()

        self._wake_fn = wake_fn

        self._lock = threading.Lock()
        self._buffer: WakingBufferRelay._Buffer = WakingBufferRelay._Buffer()

    class _Buffer:
        def __init__(self) -> None:
            self.lst: list = []
            self.age = 0

        def __repr__(self) -> str:
            return f'{self.__class__.__qualname__}({self.lst!r}, age={self.age!r})'

    def push(self, *vs: T) -> None:
        with self._lock:
            buf = self._buffer
            needs_wake = not buf.age
            buf.lst.extend(vs)
            buf.age += 1
        if needs_wake:
            self._wake_fn()

    def swap(self) -> ta.Sequence[T]:
        with self._lock:
            buf, self._buffer = self._buffer, WakingBufferRelay._Buffer()
        return buf.lst
