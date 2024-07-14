import contextlib
import functools
import threading
import typing as ta
import weakref

from . import lang


lang.warn_unstable()


TLC = ta.TypeVar('TLC', bound='ThreadLocalContext')


class ThreadLocalContext(lang.Abstract):

    _LOCAL = threading.local()

    def __init__(self) -> None:
        super().__init__()

        self._exit_stack = contextlib.ExitStack()
        self._previous: ta.Optional['ThreadLocalContext'] = None

    @property
    def previous(self) -> ta.Optional['ThreadLocalContext']:
        return self._previous

    def __enter__(self) -> 'ThreadLocalContext':
        try:
            current_by_type = self._LOCAL.current_by_type
        except AttributeError:
            current_by_type = self._LOCAL.current_by_type = weakref.WeakKeyDictionary()
        try:
            self._previous = current_by_type[type(self)]
        except KeyError:
            self._previous = None
        current_by_type[type(self)] = self
        self._exit_stack.__enter__()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> ta.Any:
        try:
            return self._exit_stack.__exit__(exc_type, exc_val, exc_tb)
        finally:
            if self.previous is None:
                del self._LOCAL.current_by_type[type(self)]
            else:
                self._LOCAL.current_by_type[type(self)] = self.previous

    @classmethod
    def current(cls: ta.Type[TLC]) -> TLC:
        try:
            return cls._LOCAL.current_by_type[cls]
        except AttributeError:
            raise KeyError


class CountDownLatch:

    def __init__(self, count: int = 1, *, reset: bool = False) -> None:
        super().__init__()

        self._count = self._initial_count = count
        self._reset = reset
        self._lock = threading.Condition()

    @property
    def count(self) -> int:
        return self._count

    @property
    def initial_count(self) -> int:
        return self._initial_count

    def count_down(self) -> None:
        with self._lock:
            if self._count < 1:
                raise ValueError(self._count)
            self._count -= 1
            if self._count == 0:
                if self._reset:
                    self._count = self._initial_count
                self._lock.notify_all()

    def wait(self, timeout: ta.Union[int, float] = -1) -> None:
        self._lock.acquire(timeout=timeout)
        try:
            while self._count > 0:
                self._lock.wait()
        finally:
            self._lock.release()


class AtomicInt(lang.Final):

    def __init__(self, value: int = 0, *, lock: lang.DefaultLockable = None) -> None:
        super().__init__()

        self._value = value
        self._lock = lang.default_lock(lock, True)

    @property
    def value(self) -> int:
        return self._value

    @value.setter
    def value(self, value: int) -> None:
        self._value = value

    def add(self, delta: int) -> int:
        with self._lock:
            self._value += delta
            return self._value

    def inc(self) -> int:
        with self._lock:
            self._value += 1
            return self._value

    def dec(self) -> int:
        with self._lock:
            self._value -= 1
            return self._value

    def get_and_add(self, delta: int) -> int:
        with self._lock:
            ret = self._value
            self._value += delta
            return ret

    def get_and_inc(self) -> int:
        with self._lock:
            ret = self._value
            self._value += 1
            return ret

    def get_and_dec(self) -> int:
        with self._lock:
            ret = self._value
            self._value -= 1
            return ret

    def cas(self, expect: int, update: int) -> bool:
        with self._lock:
            if self._value == expect:
                self._value = update
                return True
            else:
                return False

    def get_and_set(self, new: int) -> int:
        with self._lock:
            ret = self._value
            self._value = new
            return ret


class RecursionForbiddenException(RuntimeError):
    pass


def forbid_recursion(or_else: ta.Optional[ta.Callable] = None):
    def outer(fn):
        @functools.wraps(fn)
        def inner(*args, **kwargs):
            ident = threading.current_thread().ident
            if ident in idents:
                if or_else is not None:
                    return or_else(*args, **kwargs)
                raise RecursionForbiddenException(fn, args, kwargs)
            idents.add(ident)
            try:
                return fn(*args, **kwargs)
            finally:
                idents.discard(ident)
        idents = set()
        return inner
    return outer
