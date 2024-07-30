"""
TODO:
 - sync (lol) w/ asyncs.anyio
 - atomics
"""
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
