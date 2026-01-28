# ruff: noqa: UP006 UP043 UP045
# @omlish-lite
import collections
import threading
import typing as ta


T = ta.TypeVar('T')


##


class ConditionDeque(ta.Generic[T]):
    def __init__(
            self,
            *,
            cond: ta.Optional['threading.Condition'] = None,
            deque: ta.Optional[ta.Deque[T]] = None,

            lock: ta.Optional['threading.RLock'] = None,
            maxlen: ta.Optional[int] = None,
            init: ta.Optional[ta.Iterable[T]] = None,
    ) -> None:
        super().__init__()

        if cond is None:
            cond = threading.Condition(lock=lock)
        if deque is None:
            deque = collections.deque(maxlen=maxlen)
        if init:
            deque.extend(init)

        self._cond = cond
        self._deque = deque

    @property
    def cond(self) -> 'threading.Condition':
        return self._cond

    @property
    def deque(self) -> ta.Deque[T]:
        return self._deque

    def push(
            self,
            *items: T,
            n: int = 1,
    ) -> None:
        with self.cond:
            self.deque.extend(items)
            self.cond.notify(n)

    def pop(
            self,
            timeout: ta.Optional[float] = None,
            *,
            if_empty: ta.Optional[ta.Callable[[], None]] = None,
    ) -> T:
        with self.cond:
            if not self.deque and if_empty is not None:
                if_empty()
            while not self.deque:
                self.cond.wait(timeout)
            return self.deque.popleft()
