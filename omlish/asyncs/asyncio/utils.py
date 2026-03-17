# ruff: noqa: UP006 UP007 UP045
# @omlish-lite
"""
TODO:
 - split module
"""
import asyncio
import contextlib
import dataclasses as dc
import functools
import time
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
        if concurrency < 1:
            raise ValueError(f'Concurrency must be >= 1, got {concurrency}')
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


##


async def _asyncio_await_finalizer_shielded(
        awaitable: ta.Awaitable[ta.Any],
        *,
        timeout: ta.Optional[float] = None,
) -> None:
    task = asyncio.create_task(awaitable)  # type: ignore  # noqa

    if timeout is None:
        try:
            await asyncio.shield(task)
        except asyncio.CancelledError:
            try:
                await task
            finally:
                raise

    else:
        deadline = time.monotonic() + timeout

        def remaining() -> float:
            return max(0., deadline - time.monotonic())

        try:
            await asyncio.wait_for(asyncio.shield(task), timeout=remaining())
        except asyncio.CancelledError:
            try:
                await asyncio.wait_for(task, timeout=remaining())
            finally:
                raise


@dc.dataclass()
class AsyncioShieldedFinallyCancelledError(asyncio.CancelledError):
    cleanup_exc: BaseException


@contextlib.asynccontextmanager
async def asyncio_shielded_finally(
        fn: ta.Callable[[], ta.Awaitable[ta.Any]],
        *,
        timeout: ta.Optional[float] = None,
) -> ta.AsyncIterator[None]:
    raised = False

    try:
        yield

    except asyncio.CancelledError as e:
        raised = True
        try:
            await _asyncio_await_finalizer_shielded(fn(), timeout=timeout)
        except BaseException as e2:  # noqa
            raise AsyncioShieldedFinallyCancelledError(e2) from e
        else:
            raise

    except Exception as e:  # noqa
        raised = True
        try:
            await _asyncio_await_finalizer_shielded(fn(), timeout=timeout)
        except BaseException as e2:  # noqa
            raise e2 from e
        else:
            raise

    finally:
        if not raised:
            await _asyncio_await_finalizer_shielded(fn(), timeout=timeout)
