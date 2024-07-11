"""
lookit:
 - https://github.com/davidbrochart/sqlite-anyio/blob/a3ba4c6ef0535b14a5a60071fcd6ed565a514963/sqlite_anyio/sqlite.py
 - https://github.com/rafalkrupinski/ratelimit-anyio/blob/2910a8a3d6fa54ed17ee6ba457686c9f7a4c4beb/src/ratelimit_anyio/__init__.py
 - https://github.com/nekitdev/async-extensions/tree/main/async_extensions
 - https://github.com/kinnay/anynet/tree/master/anynet
 - https://github.com/M-o-a-T/asyncscope
 - https://github.com/M-o-a-T/aevent
 - https://github.com/florimondmanca/aiometer
 - https://github.com/sanitizers/octomachinery/blob/b36c3d3d49da813ac46e361424132955a4e99ac8/octomachinery/utils/asynctools.py
"""  # noqa
import typing as ta

import anyio.streams.memory

from .. import lang


T = ta.TypeVar('T')


async def anyio_eof_to_empty(fn: ta.Callable[..., ta.Awaitable[T]], *args: ta.Any, **kwargs: ta.Any) -> T | bytes:
    try:
        return await fn(*args, **kwargs)
    except anyio.EndOfStream:
        return b''


def split_memory_object_streams(
        *args: anyio.create_memory_object_stream[T],
) -> tuple[
    anyio.streams.memory.MemoryObjectSendStream[T],
    anyio.streams.memory.MemoryObjectReceiveStream[T],
]:
    [tup] = args  # type: ignore
    return tup  # type: ignore


async def gather(*fns: ta.Callable[..., ta.Awaitable[T]], take_first: bool = False) -> list[lang.Maybe[T]]:
    results = [lang.empty()] * len(fns)

    async def inner(fn, i):
        results[i] = lang.just(await fn())
        if take_first:
            tg.cancel_scope.cancel()

    async with anyio.create_task_group() as tg:
        for i, fn in enumerate(fns):
            tg.start_soon(inner, fn, i)

    return results
