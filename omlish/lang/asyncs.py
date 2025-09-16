import functools
import typing as ta


T = ta.TypeVar('T')
P = ta.ParamSpec('P')


##


def as_async(fn: ta.Callable[P, T], *, wrap: bool = False) -> ta.Callable[P, ta.Awaitable[T]]:
    async def inner(*args, **kwargs):
        return fn(*args, **kwargs)

    return functools.wraps(fn)(inner) if wrap else inner
