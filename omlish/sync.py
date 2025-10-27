# ruff: noqa: UP006 UP043 UP045
# @omlish-lite
"""
TODO:
 - sync (lol) w/ asyncs.anyio
 - atomics
 - Once poison=False, PoisonedError
"""
import collections
import threading
import typing as ta

from .lite.maybes import Maybe


T = ta.TypeVar('T')


##


class SyncOnce:
    def __init__(self) -> None:
        super().__init__()

        self._done = False
        self._lock = threading.Lock()

    def do(self, fn: ta.Callable[[], None]) -> bool:
        if self._done:
            return False
        with self._lock:
            if self._done:
                return False  # type: ignore
            try:
                fn()
            finally:
                self._done = True
            return True


##


class SyncLazy(ta.Generic[T]):
    def __init__(self) -> None:
        super().__init__()

        self._once = SyncOnce()
        self._v: Maybe[T] = Maybe.empty()

    def peek(self) -> Maybe[T]:
        return self._v

    def set(self, v: T) -> None:
        self._v = Maybe.just(v)

    def get(self, fn: ta.Callable[[], T]) -> T:
        def do():
            self._v = Maybe.just(fn())
        self._once.do(do)
        return self._v.must()


class SyncLazyFn(ta.Generic[T]):
    def __init__(self, fn: ta.Callable[[], T]) -> None:
        super().__init__()

        self._fn = fn
        self._once = SyncOnce()
        self._v: Maybe[T] = Maybe.empty()

    def peek(self) -> Maybe[T]:
        return self._v

    def set(self, v: T) -> None:
        self._v = Maybe.just(v)

    def get(self) -> T:
        def do():
            self._v = Maybe.just(self._fn())
        self._once.do(do)
        return self._v.must()


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


##


class SyncBufferRelay(ta.Generic[T]):
    def __init__(
            self,
            *,
            wake_fn: ta.Callable[[], None],
    ) -> None:
        super().__init__()

        self._wake_fn = wake_fn

        self._lock = threading.Lock()
        self._buffer: SyncBufferRelay._Buffer = SyncBufferRelay._Buffer()

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
            buf, self._buffer = self._buffer, SyncBufferRelay._Buffer()
        return buf.lst


##


class CountDownLatch:
    def __init__(self, count: int) -> None:
        super().__init__()

        self._count = count
        self._cond = threading.Condition()

    def count_down(self) -> None:
        with self._cond:
            self._count -= 1
            if self._count <= 0:
                self._cond.notify_all()

    def wait(
            self,
            timeout: ta.Optional[float] = None,
    ) -> bool:
        with self._cond:
            return self._cond.wait_for(
                lambda: self._count < 1,
                timeout,
            )
