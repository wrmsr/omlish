import asyncio
import functools
import typing as ta


CallableT = ta.TypeVar('CallableT', bound=ta.Callable)


def asyncio_once(fn: CallableT) -> CallableT:
    future = None

    @functools.wraps(fn)
    async def inner(*args, **kwargs):
        nonlocal future
        if not future:
            future = asyncio.create_task(fn(*args, **kwargs))
        return await future

    return ta.cast(CallableT, inner)
