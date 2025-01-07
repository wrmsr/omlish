import asyncio
import contextlib
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


def drain_tasks(loop=None):
    if loop is None:
        loop = asyncio.get_running_loop()

    while loop._ready or loop._scheduled:  # noqa
        loop._run_once()  # noqa


@contextlib.contextmanager
def draining_asyncio_tasks() -> ta.Iterator[None]:
    loop = asyncio.get_running_loop()
    try:
        yield
    finally:
        if loop is not None:
            drain_tasks(loop)  # noqa
