import dataclasses as dc
import functools
import time
import typing as ta


T = ta.TypeVar('T')
P = ta.ParamSpec('P')
CallableT = ta.TypeVar('CallableT', bound=ta.Callable)


##


def is_lambda(f: ta.Any) -> bool:
    l = lambda: 0
    return isinstance(f, type(l)) and f.__name__ == l.__name__


##


def maybe_call(obj: ta.Any, att: str, *args, default: ta.Any = None, **kwargs) -> ta.Any:
    try:
        fn = getattr(obj, att)
    except AttributeError:
        return default
    else:
        return fn(*args, **kwargs)


def recurse(fn: ta.Callable[..., T], *args, **kwargs) -> T:
    def rec(*args, **kwargs) -> T:
        return fn(rec, *args, **kwargs)

    return rec(*args, **kwargs)


##


def raise_(o: BaseException) -> ta.NoReturn:
    raise o


def raising(o: BaseException) -> ta.Callable[..., ta.NoReturn]:
    def inner(*args, **kwargs):
        raise o
    return inner


def try_(
        fn: ta.Callable[P, T],
        exc: type[Exception] | ta.Iterable[type[Exception]] = Exception,
        default: T | None = None,
) -> ta.Callable[P, T]:
    def inner(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except exct:
            return default

    exct = (exc,) if isinstance(exc, type) else tuple(exc)
    return inner


def finally_(fn: ta.Callable[P, T], fin: ta.Callable) -> ta.Callable[P, T]:
    def inner(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        finally:
            fin()

    return inner


##


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


def isinstance_of(class_or_tuple: ta.Any) -> ta.Callable[[ta.Any], bool]:
    return lambda o: isinstance(o, class_or_tuple)


def issubclass_of(class_or_tuple: ta.Any) -> ta.Callable[[ta.Any], bool]:
    return lambda o: issubclass(o, class_or_tuple)


##


class VoidError(Exception):
    pass


class Void:

    def __new__(cls, *args: ta.Any, **kwargs: ta.Any) -> None:  # type: ignore  # noqa
        raise VoidError

    def __init_subclass__(cls, **kwargs: ta.Any) -> None:
        raise VoidError


def void(*args: ta.Any, **kwargs: ta.Any) -> ta.NoReturn:
    raise VoidError


##


def as_async(fn: ta.Callable[P, T]) -> ta.Callable[P, ta.Awaitable[T]]:
    @functools.wraps(fn)
    async def inner(*args, **kwargs):
        return fn(*args, **kwargs)
    return inner


##


_MISSING = object()


def periodically(
        fn: CallableT,
        interval_s: float,
        initial: ta.Any = _MISSING,
        *,
        include_runtime: bool = False,
) -> CallableT:
    nxt = time.time() + interval_s
    ret = initial

    @functools.wraps(fn)
    def inner(*args, **kwargs):
        nonlocal nxt, ret
        if time.time() >= nxt or ret is _MISSING:
            if include_runtime:
                nxt = time.time() + interval_s
            ret = fn(*args, **kwargs)
            if not include_runtime:
                nxt = time.time() + interval_s
        return ret

    return inner  # type: ignore


##


@dc.dataclass(init=False)
class Args:
    args: ta.Sequence[ta.Any]
    kwargs: ta.Mapping[str, ta.Any]

    def __init__(self, *args: ta.Any, **kwargs: ta.Any) -> None:
        super().__init__()
        self.args = args
        self.kwargs = kwargs

    def __call__(self, fn: ta.Callable[..., T]) -> T:
        return fn(*self.args, **self.kwargs)
