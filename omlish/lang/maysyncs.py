import typing as ta

from ..lite.maysyncs import make_maysyncable as _make_maysyncable
from ..lite.maysyncs import maysyncable as _maysyncable


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


def make_maysyncable(
        s: ta.Callable[P, T_co],
        a: ta.Callable[P, ta.Awaitable[T_co]],
) -> MaysyncableP[P, T_co]:
    return ta.cast('MaysyncableP[P, T_co]', _make_maysyncable(
        s,
        a,
    ))


def maysyncable(m: ta.Callable[P, ta.Awaitable[T_co]]) -> MaysyncableP[P, T_co]:
    return ta.cast('MaysyncableP[P, T_co]', _maysyncable(
        m,
    ))
