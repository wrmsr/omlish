import typing as ta

from ..lite.maysyncs import make_maysync as _make_maysync
from ..lite.maysyncs import maysync as _maysync


T_co = ta.TypeVar('T_co', covariant=True)
P = ta.ParamSpec('P')


##


class MaysyncableP(ta.Protocol[P, T_co]):
    @property
    def s(self) -> ta.Callable[P, T_co]:
        ...

    @property
    def a(self) -> ta.Callable[P, ta.Awaitable[T_co]]:
        ...

    @property
    def m(self) -> ta.Callable[P, ta.Awaitable[T_co]]:
        ...


def make_maysync(
        s: ta.Callable[P, T_co],
        a: ta.Callable[P, ta.Awaitable[T_co]],
) -> MaysyncableP[P, T_co]:
    return ta.cast('MaysyncableP[P, T_co]', _make_maysync(
        s,
        a,
    ))


def maysync(m: ta.Callable[P, ta.Awaitable[T_co]]) -> MaysyncableP[P, T_co]:
    return ta.cast('MaysyncableP[P, T_co]', _maysync(
        m,
    ))
