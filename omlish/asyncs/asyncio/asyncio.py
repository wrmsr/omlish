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


def get_real_current_loop() -> asyncio.AbstractEventLoop | None:
    return asyncio.get_event_loop_policy()._local._loop  # type: ignore  # noqa


def drain_tasks(loop=None):
    if loop is None:
        loop = get_real_current_loop()

    while loop._ready or loop._scheduled:  # noqa
        loop._run_once()  # noqa


@contextlib.contextmanager
def draining_asyncio_tasks() -> ta.Iterator[None]:
    loop = get_real_current_loop()
    try:
        yield
    finally:
        if loop is not None:
            drain_tasks(loop)  # noqa
