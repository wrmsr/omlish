import typing as ta

from ..lite.maysyncs import MaysyncGenerator
from ..lite.maysyncs import Maywaitable
from ..lite.maysyncs import make_maysync as _make_maysync
from ..lite.maysyncs import maysync as _maysync
from ..lite.maysyncs import maysync_fn as _maysync_fn
from ..lite.maysyncs import maysync_generator_fn as _maysync_generator_fn
from .functions import as_async


T = ta.TypeVar('T')
O = ta.TypeVar('O')
I = ta.TypeVar('I')

P = ta.ParamSpec('P')

MaysyncFn: ta.TypeAlias = ta.Callable[P, Maywaitable[T]]
MaysyncGeneratorFn: ta.TypeAlias = ta.Callable[P, MaysyncGenerator[O, I]]


##


def make_maysync(
        s: ta.Callable[P, T],
        a: ta.Callable[P, ta.Awaitable[T]],
) -> MaysyncFn[P, T]:
    return ta.cast('MaysyncFn[P, T]', _make_maysync(
        s,
        a,
    ))


def make_maysync_from_sync(
        s: ta.Callable[P, T],
        a: ta.Callable[P, ta.Awaitable[T]] | None = None,
) -> MaysyncFn[P, T]:
    return ta.cast('MaysyncFn[P, T]', _make_maysync(
        s,
        a if a is not None else as_async(s),
    ))


##


def maysync_fn(
        m: ta.Callable[P, ta.Awaitable[T]],
) -> MaysyncFn[P, T]:
    return ta.cast('MaysyncFn[P, T]', _maysync_fn(m))


def maysync_generator_fn(
        m: ta.Callable[P, ta.AsyncGenerator[O, I]],
) -> MaysyncGeneratorFn[P, O, I]:
    return ta.cast('MaysyncGeneratorFn[P, O, I]', _maysync_generator_fn(m))


@ta.overload
def maysync(
        m: ta.Callable[P, ta.Awaitable[T]],
) -> MaysyncFn[P, T]:
    ...


@ta.overload
def maysync(
        m: ta.Callable[P, ta.AsyncGenerator[O, I]],
) -> MaysyncGeneratorFn[P, O, I]:
    ...


def maysync(m):
    return _maysync(m)
