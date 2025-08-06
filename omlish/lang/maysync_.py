import functools
import typing as ta

from ..lite.maysync import MaysyncGen
from ..lite.maysync import a_maysync
from ..lite.maysync import maysync


T = ta.TypeVar('T')
P = ta.ParamSpec('P')


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
