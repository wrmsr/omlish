# ruff: noqa: UP006 UP043 UP045
# @omlish-lite
import threading
import typing as ta

from ..lite.maybes import Maybe


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
