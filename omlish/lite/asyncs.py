# ruff: noqa: UP045
import functools
import typing as ta


T = ta.TypeVar('T')


##


async def opt_await(aw: ta.Optional[ta.Awaitable[T]]) -> ta.Optional[T]:
    return (await aw if aw is not None else None)


def as_async(fn: ta.Callable[..., T], *, wrap: bool = False) -> ta.Callable[..., ta.Awaitable[T]]:
    async def inner(*args, **kwargs):
        return fn(*args, **kwargs)

    return functools.wraps(fn)(inner) if wrap else inner
