# ruff: noqa: UP006 UP007
# @omlish-lite
import asyncio
import contextlib
import functools
import typing as ta


T = ta.TypeVar('T')

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


def drain_asyncio_tasks(loop=None):
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
            drain_asyncio_tasks(loop)  # noqa


async def asyncio_wait_concurrent(
        coros: ta.Iterable[ta.Awaitable[T]],
        concurrency: ta.Union[int, asyncio.Semaphore],
        *,
        return_when: ta.Any = asyncio.FIRST_EXCEPTION,
) -> ta.List[T]:
    if isinstance(concurrency, asyncio.Semaphore):
        semaphore = concurrency
    elif isinstance(concurrency, int):
        semaphore = asyncio.Semaphore(concurrency)
    else:
        raise TypeError(concurrency)

    async def limited_task(coro):
        async with semaphore:
            return await coro

    tasks = [asyncio.create_task(limited_task(coro)) for coro in coros]
    done, pending = await asyncio.wait(tasks, return_when=return_when)

    for task in pending:
        task.cancel()

    for task in done:
        if task.exception():
            raise task.exception()  # type: ignore

    return [task.result() for task in done]
