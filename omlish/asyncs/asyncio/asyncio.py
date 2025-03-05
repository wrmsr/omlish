# ruff: noqa: UP006 UP007
# @omlish-lite
"""
TODO:
 - split module
"""
import asyncio
import contextlib
import functools
import typing as ta


T = ta.TypeVar('T')

CallableT = ta.TypeVar('CallableT', bound=ta.Callable)


##


def asyncio_ensure_task(obj: ta.Awaitable) -> asyncio.Task:
    if isinstance(obj, asyncio.Task):
        return obj
    elif isinstance(obj, ta.Coroutine):
        return asyncio.create_task(obj)
    else:
        raise TypeError(obj)


##


def asyncio_once(fn: CallableT) -> CallableT:
    task = None

    @functools.wraps(fn)
    async def inner(*args, **kwargs):
        nonlocal task
        if not task:
            task = asyncio.create_task(fn(*args, **kwargs))
        return await task

    return ta.cast(CallableT, inner)


##


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


##


async def asyncio_wait_concurrent(
        awaitables: ta.Iterable[ta.Awaitable[T]],
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

    async def limited_task(a):
        async with semaphore:
            return await a

    futs = [asyncio.create_task(limited_task(a)) for a in awaitables]
    done, pending = await asyncio.wait(futs, return_when=return_when)

    for fut in pending:
        fut.cancel()

    for fut in done:
        if fut.exception():
            raise fut.exception()  # type: ignore

    return [fut.result() for fut in done]


async def asyncio_wait_maybe_concurrent(
        awaitables: ta.Iterable[ta.Awaitable[T]],
        concurrency: ta.Union[int, asyncio.Semaphore, None],
) -> ta.List[T]:
    # Note: Only supports return_when=asyncio.FIRST_EXCEPTION
    if concurrency is None:
        return [await a for a in awaitables]

    else:
        return await asyncio_wait_concurrent(awaitables, concurrency)
