import typing as ta

from ..lite.maysyncs import Maywaitable
from ..lite.maysyncs import make_maysync as _make_maysync
from ..lite.maysyncs import maysync as _maysync
from .functions import as_async


T = ta.TypeVar('T')
P = ta.ParamSpec('P')

MaysyncFnP: ta.TypeAlias = ta.Callable[P, Maywaitable[T]]


##


def make_maysync(
        s: ta.Callable[P, T],
        a: ta.Callable[P, ta.Awaitable[T]],
) -> MaysyncFnP[P, T]:
    return ta.cast('MaysyncFnP[P, T]', _make_maysync(
        s,
        a,
    ))


def make_maysync_from_sync(
        s: ta.Callable[P, T],
        a: ta.Callable[P, ta.Awaitable[T]] | None = None,
) -> MaysyncFnP[P, T]:
    return ta.cast('MaysyncFnP[P, T]', _make_maysync(
        s,
        a if a is not None else as_async(s),
    ))


##


def maysync(m: ta.Callable[P, ta.Awaitable[T]]) -> MaysyncFnP[P, T]:
    return ta.cast('MaysyncFnP[P, T]', _maysync(
        m,
    ))
