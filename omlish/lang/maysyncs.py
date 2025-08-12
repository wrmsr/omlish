import typing as ta

from ..lite.maysyncs import make_maysync as _make_maysync
from ..lite.maysyncs import maysync as _maysync
from .functions import as_async


T_co = ta.TypeVar('T_co', covariant=True)
P = ta.ParamSpec('P')


##


class MaysyncableP(ta.Protocol[P, T_co]):
    def __get__(self, instance: ta.Any, owner: ta.Any = None) -> 'MaysyncableP[P, T_co]':
        ...

    def s(self, *args: P.args, **kwargs: P.kwargs) -> T_co:
        ...

    def a(self, *args: P.args, **kwargs: P.kwargs) -> ta.Awaitable[T_co]:
        ...

    def m(self, *args: P.args, **kwargs: P.kwargs) -> ta.Awaitable[T_co]:
        ...


def make_maysync(
        s: ta.Callable[P, T_co],
        a: ta.Callable[P, ta.Awaitable[T_co]] | None = None,
) -> MaysyncableP[P, T_co]:
    return ta.cast('MaysyncableP[P, T_co]', _make_maysync(
        s,
        a if a is not None else as_async(s),
    ))


def maysync(m: ta.Callable[P, ta.Awaitable[T_co]]) -> MaysyncableP[P, T_co]:
    return ta.cast('MaysyncableP[P, T_co]', _maysync(
        m,
    ))
