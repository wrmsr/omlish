"""
TODO:
 - sync (lol) w/ asyncs.anyio
 - atomics
"""
import collections
import threading
import typing as ta

from . import lang


T = ta.TypeVar('T')


class Once:
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


class Lazy(ta.Generic[T]):
    def __init__(self) -> None:
        super().__init__()
        self._once = Once()
        self._v: lang.Maybe[T] = lang.empty()

    def peek(self) -> lang.Maybe[T]:
        return self._v

    def set(self, v: T) -> None:
        self._v = lang.just(v)

    def get(self, fn: ta.Callable[[], T]) -> T:
        def do():
            self._v = lang.just(fn())
        self._once.do(do)
        return self._v.must()


class LazyFn(ta.Generic[T]):
    def __init__(self, fn: ta.Callable[[], T]) -> None:
        super().__init__()
        self._fn = fn
        self._once = Once()
        self._v: lang.Maybe[T] = lang.empty()

    def peek(self) -> lang.Maybe[T]:
        return self._v

    def set(self, v: T) -> None:
        self._v = lang.just(v)

    def get(self) -> T:
        def do():
            self._v = lang.just(self._fn())
        self._once.do(do)
        return self._v.must()


class ConditionDeque(ta.Generic[T]):
    def __init__(
            self,
            *,
            cond: ta.Optional['threading.Condition'] = None,
            deque: collections.deque[T] | None = None,

            lock: ta.Optional['threading.RLock'] = None,
            maxlen: int | None = None,
            init: ta.Iterable[T] | None = None,
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
    def deque(self) -> collections.deque[T]:
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
            timeout: float | None = None,
            *,
            if_empty: ta.Callable[[], None] | None = None,
    ) -> T:
        with self.cond:
            if not self.deque and if_empty is not None:
                if_empty()
            while not self.deque:
                self.cond.wait(timeout)
            return self.deque.popleft()
