import functools
import time
import typing as ta

from .descriptors import is_method_descriptor


T = ta.TypeVar('T')


def is_lambda(f: ta.Any) -> bool:
    l = lambda: 0
    return isinstance(f, type(l)) and f.__name__ == l.__name__


def maybe_call(obj: ta.Any, att: str, *args, default: ta.Any = None, **kwargs) -> ta.Any:
    try:
        fn = getattr(obj, att)
    except AttributeError:
        return default
    else:
        return fn(*args, **kwargs)


def unwrap_func(fn: ta.Callable) -> ta.Callable:
    fn, _ = unwrap_func_with_partials(fn)
    return fn


def unwrap_func_with_partials(fn: ta.Callable) -> tuple[ta.Callable, list[functools.partial]]:
    ps = []
    while True:
        if is_method_descriptor(fn):
            fn = fn.__func__  # type: ignore
        elif isinstance(fn, functools.partial):
            ps.append(fn)
            fn = fn.func
        else:
            nxt = getattr(fn, '__wrapped__', None)
            if not callable(nxt):
                break
            elif nxt is fn:
                raise TypeError(fn)
            fn = nxt
    return fn, ps


def raise_(o: BaseException) -> ta.NoReturn:
    raise o


def try_(
        exc: ta.Union[type[Exception], ta.Iterable[type[Exception]]] = Exception,
        default: ta.Optional[T] = None,
) -> ta.Callable[..., T]:
    def outer(fn):
        def inner(*args, **kwargs):
            try:
                return fn(*args, **kwargs)
            except exct:
                return default

        return inner

    exct = (exc,) if isinstance(exc, type) else tuple(exc)
    return outer


def recurse(fn: ta.Callable[..., T], *args, **kwargs) -> T:
    def rec(*args, **kwargs) -> T:
        return fn(rec, *args, **kwargs)

    return rec(*args, **kwargs)


def identity(obj: T) -> T:
    return obj


class constant(ta.Generic[T]):  # noqa

    def __init__(self, obj: T) -> None:
        super().__init__()

        self._obj = obj

    def __call__(self) -> T:
        return self._obj


def is_none(o: ta.Any) -> bool:
    return o is None


def is_not_none(o: ta.Any) -> bool:
    return o is not None


class VoidException(Exception):
    pass


class Void:

    def __new__(cls, *args, **kwargs):
        raise VoidException

    def __init_subclass__(cls, **kwargs):
        raise VoidException


def void(*args, **kwargs) -> ta.NoReturn:
    raise VoidException


def ticking_timeout(
        s: int | float | None,
        ex: type[BaseException] | BaseException = TimeoutError,
) -> ta.Callable[[], None]:
    if s is None:
        return lambda: None
    def tick():  # noqa
        if time.time() >= deadline:
            raise ex
    deadline = time.time() + s
    return tick
