"""
TODO:
 - AsyncExitStacked
 - lol does double_check_setdefault need a CowDict in FT?
 - AsyncLockable, DefaultAsyncLockable
"""
import abc
import contextlib
import contextvars
import functools
import threading
import time
import types
import typing as ta

from ..lite.abstract import Abstract


T = ta.TypeVar('T')
K = ta.TypeVar('K')
V = ta.TypeVar('V')

P = ta.ParamSpec('P')


##


class ContextManaged(Abstract):
    def __enter__(self):
        return None

    def __exit__(
            self,
            exc_type: type[BaseException] | None,
            exc_val: BaseException | None,
            exc_tb: types.TracebackType | None,
    ) -> bool | None:
        return None


class SelfContextManaged(ContextManaged):
    def __enter__(self) -> ta.Self:
        return self


class ValueContextManager(ContextManaged, ta.Generic[T]):
    def __init__(self, value: T) -> None:
        super().__init__()

        self._value = value

    def __enter__(self) -> T:
        return self._value


NOP_CONTEXT_MANAGER = ValueContextManager(None)


#


class AsyncContextManaged(Abstract):
    async def __aenter__(self):
        return None

    async def __aexit__(
            self,
            exc_type: type[BaseException] | None,
            exc_val: BaseException | None,
            exc_tb: types.TracebackType | None,
    ) -> bool | None:
        return None


class SelfAsyncContextManaged(AsyncContextManaged):
    async def __aenter__(self) -> ta.Self:
        return self


class ValueAsyncContextManager(AsyncContextManaged, ta.Generic[T]):
    def __init__(self, value: T) -> None:
        super().__init__()

        self._value = value

    async def __aenter__(self) -> T:
        return self._value


NOP_ASYNC_CONTEXT_MANAGER = ValueAsyncContextManager(None)


##


class ContextManager(Abstract, ta.Generic[T]):
    def __init_subclass__(cls, **kwargs: ta.Any) -> None:
        super().__init_subclass__(**kwargs)

        if not hasattr(cls.__contextmanager__, '_is_contextmanager'):
            cls.__contextmanager__ = contextlib.contextmanager(cls.__contextmanager__)  # type: ignore  # noqa
            cls.__contextmanager__._is_contextmanager = True  # type: ignore  # noqa

    @abc.abstractmethod
    def __contextmanager__(self) -> ta.Iterable[T]:
        raise NotImplementedError

    __contextmanager__._is_contextmanager = True  # type: ignore  # noqa

    _contextmanager: ta.Any

    def __enter__(self) -> T:
        self._contextmanager = self.__contextmanager__()
        return self._contextmanager.__enter__()

    def __exit__(
            self,
            exc_type: type[BaseException] | None,
            exc_val: BaseException | None,
            exc_tb: types.TracebackType | None,
    ) -> bool | None:
        return self._contextmanager.__exit__(exc_type, exc_val, exc_tb)


#


class AsyncContextManager(Abstract, ta.Generic[T]):
    def __init_subclass__(cls, **kwargs: ta.Any) -> None:
        super().__init_subclass__(**kwargs)

        if not hasattr(cls.__asynccontextmanager__, '_is_asynccontextmanager'):
            cls.__asynccontextmanager__ = contextlib.asynccontextmanager(cls.__asynccontextmanager__)  # type: ignore  # noqa
            cls.__asynccontextmanager__._is_asynccontextmanager = True  # type: ignore  # noqa

    @abc.abstractmethod
    def __asynccontextmanager__(self) -> ta.AsyncIterator[T]:
        raise NotImplementedError

    __asynccontextmanager__._is_asynccontextmanager = True  # type: ignore  # noqa

    _asynccontextmanager: ta.Any

    async def __aenter__(self) -> T:
        self._asynccontextmanager = self.__asynccontextmanager__()
        return await self._asynccontextmanager.__aenter__()

    async def __aexit__(
            self,
            exc_type: type[BaseException] | None,
            exc_val: BaseException | None,
            exc_tb: types.TracebackType | None,
    ) -> None:
        return await self._asynccontextmanager.__aexit__(exc_type, exc_val, exc_tb)


##


@contextlib.contextmanager
def maybe_managing(obj: T) -> ta.Iterator[T]:
    if isinstance(obj, ta.ContextManager):
        with obj:
            yield obj
    else:
        yield obj


@contextlib.asynccontextmanager
async def async_maybe_managing(obj: T) -> ta.AsyncGenerator[T]:
    if isinstance(obj, ta.AsyncContextManager):
        async with obj:
            yield obj
    else:
        yield obj


@contextlib.asynccontextmanager
async def async_or_sync_maybe_managing(obj: T) -> ta.AsyncGenerator[T]:
    if isinstance(obj, ta.AsyncContextManager):
        async with obj:
            yield obj
    elif isinstance(obj, ta.ContextManager):
        with obj:
            yield obj
    else:
        yield obj


##


@contextlib.contextmanager
def disposing(obj: T, attr: str = 'dispose') -> ta.Iterator[T]:
    try:
        yield obj
    finally:
        getattr(obj, attr)()


@contextlib.contextmanager
def breakpoint_on_exception():  # noqa
    try:
        yield
    except Exception as e:  # noqa
        breakpoint()  # noqa
        raise


@contextlib.contextmanager
def context_var_setting(var: contextvars.ContextVar[T], val: T) -> ta.Iterator[T]:
    token = var.set(val)
    try:
        yield val
    finally:
        var.reset(token)


##


ContextWrappable: ta.TypeAlias = ta.ContextManager | str | ta.Callable[..., ta.ContextManager]


class ContextWrapped:
    def __init__(self, fn: ta.Callable, cm: str | ContextWrappable) -> None:
        super().__init__()

        self._fn = (fn,)
        self._cm = cm
        self._name: str | None = None

        functools.update_wrapper(self, fn)

    @property
    def _fn(self):
        return self.__fn

    @_fn.setter
    def _fn(self, x):
        self.__fn = x

    def __set_name__(self, owner, name):
        if name is not None:
            if self._name is not None:
                if name != self._name:
                    raise NameError(name, self._name)
            else:
                self._name = name

    def __get__(self, instance, owner=None):
        if instance is None and owner is None:
            return self
        fn = self._fn[0].__get__(instance, owner)  # noqa
        cm: ta.Any = self._cm
        if isinstance(self._cm, str):
            if instance is not None:
                cm = getattr(instance, cm)
            elif owner is not None:
                cm = getattr(owner, cm)
            else:
                raise TypeError(cm)
        elif hasattr(cm, '__enter__'):
            pass
        elif callable(cm):
            cm = cm.__get__(instance, owner)  # noqa
        else:
            raise TypeError(cm)
        ret = type(self)(fn, cm)
        if self._name is not None:
            with contextlib.suppress(TypeError):
                instance.__dict__[self._name] = ret
        return ret

    def __call__(self, *args, **kwargs):
        if isinstance(self._cm, str):
            raise TypeError(self._cm)
        cm = self._cm
        if not hasattr(cm, '__enter__') and callable(cm):
            cm = cm(*args, **kwargs)
        with cm:  # type: ignore
            return self._fn[0](*args, **kwargs)


def context_wrapped(cm):  # ContextWrappable -> ta.Callable[[CallableT], CallableT]:  # noqa
    def inner(fn):
        return ContextWrapped(fn, cm)
    return inner


##


Lockable = ta.Callable[[], ta.ContextManager]
DefaultLockable = bool | Lockable | ta.ContextManager | None


def default_lock(value: DefaultLockable, default: DefaultLockable = None) -> Lockable:
    if value is None:
        value = default

    if value is True:
        lock = threading.RLock()
        return lambda: lock

    elif value is False or value is None:
        return lambda: NOP_CONTEXT_MANAGER

    elif callable(value):
        return value

    elif isinstance(value, ta.ContextManager):
        return lambda: value

    else:
        raise TypeError(value)


#


AsyncLockable = ta.Callable[[], ta.AsyncContextManager]
DefaultAsyncLockable = AsyncLockable | ta.AsyncContextManager | None


def default_async_lock(value: DefaultAsyncLockable, default: DefaultAsyncLockable = None) -> AsyncLockable:
    if value is None:
        value = default

    if value is None:
        return lambda: NOP_ASYNC_CONTEXT_MANAGER

    elif callable(value):
        return value

    elif isinstance(value, ta.AsyncContextManager):
        return lambda: value

    else:
        raise TypeError(value)


##


class Timer:
    def __init__(
            self,
            clock: ta.Callable[[], float] | None = None,
    ) -> None:
        super().__init__()

        self._clock = clock if clock is not None else time.monotonic

    _start: float
    _end: float

    @property
    def start(self) -> float:
        return self._start

    @property
    def end(self) -> float:
        return self._end

    @property
    def elapsed(self) -> float:
        return self._end - self._start

    def __enter__(self) -> ta.Self:
        self._start = self._clock()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._end = self._clock()


##


def double_check_setdefault(
        cm: ta.ContextManager,
        dct: ta.MutableMapping[K, V],
        k: K,
        fn: ta.Callable[[], V],
) -> V:
    try:
        return dct[k]
    except KeyError:
        pass

    with cm:
        try:
            return dct[k]
        except KeyError:
            pass

        v = fn()
        dct[k] = v
        return v


##


def call_with_exit_stack(
        fn: ta.Callable[ta.Concatenate[contextlib.ExitStack, P], T],
        *args: P.args,
        **kwargs: P.kwargs,
) -> T:
    with contextlib.ExitStack() as es:
        return fn(es, *args, **kwargs)


async def call_with_async_exit_stack(
        fn: ta.Callable[ta.Concatenate[contextlib.AsyncExitStack, P], ta.Awaitable[T]],
        *args: P.args,
        **kwargs: P.kwargs,
) -> T:
    async with contextlib.AsyncExitStack() as aes:
        return await fn(aes, *args, **kwargs)


def with_exit_stack(
        fn: ta.Callable[ta.Concatenate[contextlib.ExitStack, P], T],
) -> ta.Callable[P, T]:
    return functools.partial(call_with_exit_stack, fn)


def with_async_exit_stack(
        fn: ta.Callable[ta.Concatenate[contextlib.AsyncExitStack, P], ta.Awaitable[T]],
) -> ta.Callable[P, ta.Awaitable[T]]:
    return functools.partial(call_with_async_exit_stack, fn)
