import functools
import typing as ta

from .descriptors import is_method_descriptor


T = ta.TypeVar('T')


def unwrap_func(fn: ta.Callable) -> ta.Callable:
    while True:
        if is_method_descriptor(fn):
            fn = fn.__func__  # type: ignore
        elif isinstance(fn, functools.partial):
            fn = fn.func
        else:
            nxt = getattr(fn, '__wrapped__', None)
            if not callable(nxt):
                return fn
            elif nxt is fn:
                raise TypeError(fn)
            fn = nxt


def raise_(o: BaseException) -> ta.NoReturn:
    raise o


def try_(
        exc: ta.Union[ta.Type[Exception], ta.Iterable[ta.Type[Exception]]] = Exception,
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


def cmp(l: ta.Any, r: ta.Any) -> int:
    return int(l > r) - int(l < r)
