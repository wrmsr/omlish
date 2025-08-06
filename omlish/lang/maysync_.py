import functools
import typing as ta

from ..lite.maysync import MaysyncGen
from ..lite.maysync import MaysyncOp
from ..lite.maysync import a_maysync
from ..lite.maysync import maysync


T = ta.TypeVar('T')
P = ta.ParamSpec('P')


##


def maysync_op(
        fn: ta.Callable[P, T],
        a_fn: ta.Callable[P, ta.Awaitable[T]],
) -> MaysyncOp[T]:
    return MaysyncOp(
        fn,
        a_fn,
    )


##


def maysync_yield(
        fn: ta.Callable[P, T],
        a_fn: ta.Callable[P, ta.Awaitable[T]],
) -> ta.Callable[P, ta.Generator[ta.Any, ta.Any, T]]:
    def inner(*args, **kwargs):
        return (yield MaysyncOp(fn, a_fn)(*args, **kwargs))
    return inner


##


def maysync_wrap(fn: ta.Callable[P, MaysyncGen[T]]) -> ta.Callable[P, T]:
    @functools.wraps(fn)
    def inner(*args, **kwargs):
        return maysync(fn, *args, **kwargs)
    return inner


def a_maysync_wrap(fn: ta.Callable[P, MaysyncGen[T]]) -> ta.Callable[P, ta.Awaitable[T]]:
    @functools.wraps(fn)
    async def inner(*args, **kwargs):
        return await a_maysync(fn, *args, **kwargs)
    return inner
