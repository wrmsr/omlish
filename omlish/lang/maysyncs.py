import typing as ta

from ..lite.maysyncs import Maywaitable
from ..lite.maysyncs import make_maysync as _make_maysync
from ..lite.maysyncs import maysync as _maysync
from .functions import as_async


T = ta.TypeVar('T')
T_co = ta.TypeVar('T_co', covariant=True)
P = ta.ParamSpec('P')

MaysyncP: ta.TypeAlias = ta.Callable[P, Maywaitable[T]]


##


def make_maysync(
        s: ta.Callable[P, T_co],
        a: ta.Callable[P, ta.Awaitable[T_co]] | None = None,
) -> MaysyncP[P, T_co]:
    return ta.cast('MaysyncP[P, T_co]', _make_maysync(
        s,
        a if a is not None else as_async(s),
    ))


def maysync(m: ta.Callable[P, ta.Awaitable[T_co]]) -> MaysyncP[P, T_co]:
    return ta.cast('MaysyncP[P, T_co]', _maysync(
        m,
    ))
