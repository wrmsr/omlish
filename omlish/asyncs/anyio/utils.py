import functools
import typing as ta

import anyio.abc
import sniffio

from ... import lang


P = ta.ParamSpec('P')
T = ta.TypeVar('T')


##


async def eof_to_empty(fn: ta.Callable[..., ta.Awaitable[T]], *args: ta.Any, **kwargs: ta.Any) -> T | bytes:
    try:
        return await fn(*args, **kwargs)
    except anyio.EndOfStream:
        return b''


async def gather(*fns: ta.Callable[..., ta.Awaitable[T]], take_first: bool = False) -> list[lang.Maybe[T]]:
    results: list[lang.Maybe[T]] = [lang.empty()] * len(fns)

    async def inner(fn, i):
        results[i] = lang.just(await fn())
        if take_first:
            tg.cancel_scope.cancel()

    async with anyio.create_task_group() as tg:
        for i, fn in enumerate(fns):
            tg.start_soon(inner, fn, i)

    return results


async def first(*fns: ta.Callable[..., ta.Awaitable[T]], **kwargs: ta.Any) -> list[lang.Maybe[T]]:
    return await gather(*fns, take_first=True, **kwargs)


##


def get_current_task() -> anyio.TaskInfo | None:
    try:
        return anyio.get_current_task()
    except sniffio.AsyncLibraryNotFoundError:
        return None


##


async def call_with_task_group(
        fn: ta.Callable[ta.Concatenate[anyio.abc.TaskGroup, P], ta.Awaitable[T]],
        *args: ta.Any,
        **kwargs: ta.Any,
) -> T:
    async with anyio.create_task_group() as tg:
        return await fn(tg, *args, **kwargs)


def run_with_task_group(
        fn: ta.Callable[ta.Concatenate[anyio.abc.TaskGroup, P], ta.Awaitable[T]],
        *args: ta.Any,
        **kwargs: ta.Any,
) -> T:
    return anyio.run(
        functools.partial(call_with_task_group, fn, *args),
        **kwargs,
    )
