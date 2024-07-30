"""
TODO:
 - bane
  - owned lock
  - async once

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
import anyio.streams.stapled

from .. import check
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
    [tup] = args
    return tup


# FIXME: https://github.com/python/mypy/issues/15238
# FIXME: https://youtrack.jetbrains.com/issues?q=tag:%20%7BPEP%20695%7D
def create_memory_object_stream[T](max_buffer_size: float = 0) -> tuple[
    anyio.streams.memory.MemoryObjectSendStream[T],
    anyio.streams.memory.MemoryObjectReceiveStream[T],
]:
    return anyio.create_memory_object_stream[T](max_buffer_size)  # noqa


def staple_memory_object_stream(
        *args: anyio.create_memory_object_stream[T],
) -> anyio.streams.stapled.StapledObjectStream[T]:
    send, receive = args
    return anyio.streams.stapled.StapledObjectStream(
        check.isinstance(send, anyio.streams.memory.MemoryObjectSendStream),  # type: ignore
        check.isinstance(receive, anyio.streams.memory.MemoryObjectReceiveStream),  # type: ignore
    )


# FIXME: https://github.com/python/mypy/issues/15238
# FIXME: https://youtrack.jetbrains.com/issues?q=tag:%20%7BPEP%20695%7D
def staple_memory_object_stream2[T](max_buffer_size: float = 0) -> anyio.streams.stapled.StapledObjectStream[T]:
    send, receive = anyio.create_memory_object_stream[T](max_buffer_size)
    return anyio.streams.stapled.StapledObjectStream(
        check.isinstance(send, anyio.streams.memory.MemoryObjectSendStream),  # type: ignore
        check.isinstance(receive, anyio.streams.memory.MemoryObjectReceiveStream),  # type: ignore
    )


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


class Once:
    def __init__(self) -> None:
        super().__init__()
        self._done = False
        self._lock = anyio.Lock()

    async def do(self, fn: ta.Callable[[], ta.Awaitable[None]]) -> bool:
        if self._done:
            return False
        async with self._lock:
            if self._done:
                return False  # type: ignore
            try:
                await fn()
            finally:
                self._done = True
            return True


class Lazy(ta.Generic[T]):
    def __init__(self) -> None:
        super().__init__()
        self._once = Once()
        self._v: lang.Maybe[T] = lang.empty()

    def peek(self) -> lang.Maybe[T]:
        return self._v

    def set(self, v: T) -> None:
        self._v = lang.just(v)

    async def get(self, fn: ta.Callable[[], ta.Awaitable[T]]) -> T:
        async def do():
            self._v = lang.just(await fn())
        await self._once.do(do)
        return self._v.must()


class LazyFn(ta.Generic[T]):
    def __init__(self, fn: ta.Callable[[], ta.Awaitable[T]]) -> None:
        super().__init__()
        self._fn = fn
        self._once = Once()
        self._v: lang.Maybe[T] = lang.empty()

    def peek(self) -> lang.Maybe[T]:
        return self._v

    def set(self, v: T) -> None:
        self._v = lang.just(v)

    async def get(self) -> T:
        async def do():
            self._v = lang.just(await self._fn())
        await self._once.do(do)
        return self._v.must()
