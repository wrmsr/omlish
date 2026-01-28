# ruff: noqa: UP006 UP043 UP045
# @omlish-lite
import contextlib
import threading
import typing as ta


T = ta.TypeVar('T')


##


class ObjectPool(ta.Generic[T]):
    def __init__(self, new: ta.Optional[ta.Callable[[], T]] = None) -> None:
        super().__init__()

        self._new = new

        self._lock = threading.Lock()
        self._pool: ta.List[T] = []
        self._closed: bool = False

    #

    class ClosedError(Exception):
        pass

    def _check_not_closed(self) -> None:
        if self._closed:
            raise ObjectPool.ClosedError

    def close(self) -> None:
        with self._lock:
            self._closed = True

    #

    class EmptyError(Exception):
        pass

    def get(self, new: ta.Optional[ta.Callable[[], T]] = None) -> T:
        with self._lock:
            self._check_not_closed()
            if self._pool:
                return self._pool.pop()

        if new is None:
            new = self._new
        if new is not None:
            return new()

        raise ObjectPool.EmptyError

    def put(self, obj: T) -> None:
        with self._lock:
            self._check_not_closed()
            self._pool.append(obj)

    def acquire(self, new: ta.Optional[ta.Callable[[], T]] = None) -> ta.ContextManager[T]:
        @contextlib.contextmanager
        def inner():
            o = self.get(new)
            try:
                yield o
            finally:
                self.put(o)

        return inner()

    def drain(self) -> ta.List[T]:
        with self._lock:
            out = self._pool
            self._pool = []

        return out

    #

    def manage(
            self,
            drain: ta.Optional[ta.Callable[[T], None]] = None,
    ) -> ta.ContextManager['ObjectPool[T]']:
        @contextlib.contextmanager
        def inner():
            with self._lock:
                self._check_not_closed()

            try:
                yield self

            finally:
                self.close()

                if drain is not None:
                    for o in self.drain():
                        drain(o)

        return inner()
