import abc
import functools
import typing as ta

from ..lite.abstract import Abstract
from ..lite.asyncs import sync_await as _sync_await
from ..lite.maybes import Maybe


O = ta.TypeVar('O')
I = ta.TypeVar('I')
R = ta.TypeVar('R')
T = ta.TypeVar('T')
P = ta.ParamSpec('P')


##


def as_async(fn: ta.Callable[P, T], *, wrap: bool = False) -> ta.Callable[P, ta.Awaitable[T]]:
    async def inner(*args, **kwargs):
        return fn(*args, **kwargs)

    return functools.wraps(fn)(inner) if wrap else inner


##


class AsyncGeneratorWithReturn(ta.AsyncGenerator[O, I], Abstract, ta.Generic[O, I, R]):
    @property
    @abc.abstractmethod
    def value(self) -> Maybe[R]:
        raise NotImplementedError


@ta.final
class _AsyncGeneratorWithReturn(AsyncGeneratorWithReturn[O, I, R]):
    def __init__(self, ag: ta.AsyncGenerator[O, I]) -> None:
        if isinstance(ag, _AsyncGeneratorWithReturn):
            raise TypeError(ag)
        self._ag = ag

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self._ag!r})'

    _v: Maybe[R] = Maybe.empty()

    @property
    def value(self) -> Maybe[R]:
        return self._v

    def _set_value(self, v: R) -> None:
        if self._v.present:
            raise TypeError('Return value already set')
        self._v = Maybe.just(v)

    def __anext__(self):
        return self._ag.__anext__()

    def asend(self, value):
        return self._ag.asend(value)

    def athrow(self, typ, val=None, tb=None):
        return self._ag.athrow(typ, val, tb)

    def aclose(self):
        return self._ag.aclose()


def async_generator_with_return(
        fn: ta.Callable[ta.Concatenate[ta.Callable[[R], None], P], ta.AsyncGenerator[O, I]],
) -> ta.Callable[P, AsyncGeneratorWithReturn[O, I, R]]:
    @functools.wraps(fn)
    def inner(*args, **kwargs):
        def set_value(v):
            x._set_value(v)  # noqa

        return (x := _AsyncGeneratorWithReturn(fn(set_value, *args, **kwargs)))  # type: ignore[var-annotated]

    return inner


##


sync_await = _sync_await


try:
    from . import _asyncs as cext  # type: ignore

except ImportError:
    pass

else:
    sync_await = cext.sync_await
