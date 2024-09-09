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

==

async def killer(shutdown: anyio.Event, sleep_s: float) -> None:
    log.warning('Killing in %d seconds', sleep_s)
    await anyio.sleep(sleep_s)
    log.warning('Killing')
    shutdown.set()

"""  # noqa
import dataclasses as dc
import signal
import typing as ta

import anyio.abc
import anyio.streams.memory
import anyio.streams.stapled
import sniffio

from .. import check
from .. import lang


T = ta.TypeVar('T')

MemoryObjectReceiveStream: ta.TypeAlias = anyio.streams.memory.MemoryObjectReceiveStream
MemoryObjectSendStream: ta.TypeAlias = anyio.streams.memory.MemoryObjectSendStream

StapledByteStream: ta.TypeAlias = anyio.streams.stapled.StapledByteStream
StapledObjectStream: ta.TypeAlias = anyio.streams.stapled.StapledObjectStream


@dc.dataclass(eq=False)
class MemoryStapledObjectStream(StapledObjectStream[T]):
    send_stream: MemoryObjectSendStream[T]
    receive_stream: MemoryObjectReceiveStream[T]


##


async def anyio_eof_to_empty(fn: ta.Callable[..., ta.Awaitable[T]], *args: ta.Any, **kwargs: ta.Any) -> T | bytes:
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


#


BackendTask: ta.TypeAlias = ta.Union[  # noqa
    # asyncio.tasks.Task,
    # trio.lowlevel.Task,
    ta.Any,
]


def _is_class_named(obj: ta.Any, m: str, n: str) -> bool:
    cls = obj.__class__
    return cls.__module__ == m and cls.__name__ == n


def get_backend_task(at: anyio.TaskInfo) -> BackendTask | None:
    if _is_class_named(at, 'anyio._backends._asyncio', 'AsyncIOTaskInfo'):
        # https://github.com/agronholm/anyio/blob/8907964926a24461840eee0925d3f355e729f15d/src/anyio/_backends/_asyncio.py#L1846  # noqa
        # weakref.ref
        obj = at._task()  # type: ignore  # noqa
        if obj is not None and not (
                _is_class_named(obj, '_asyncio', 'Task') or
                _is_class_named(obj, 'asyncio.tasks', 'Task')
        ):
            raise TypeError(obj)
        return obj

    elif _is_class_named(at, 'anyio._backends._trio', 'TrioTaskInfo'):
        # https://github.com/agronholm/anyio/blob/8907964926a24461840eee0925d3f355e729f15d/src/anyio/_backends/_trio.py#L850  # noqa
        # weakref.proxy
        # https://stackoverflow.com/a/62144308 :|
        obj = at._task.__repr__.__self__  # type: ignore  # noqa
        if obj is not None and not _is_class_named(obj, 'trio.lowlevel', 'Task'):
            raise TypeError(obj)
        return obj

    else:
        raise TypeError(at)


def get_current_backend_task() -> BackendTask | None:
    if (at := get_current_task()) is not None:
        return get_backend_task(at)
    else:
        return None


##


def split_memory_object_streams(
        *args: anyio.create_memory_object_stream[T],
) -> tuple[
    MemoryObjectSendStream[T],
    MemoryObjectReceiveStream[T],
]:
    [tup] = args
    return tup


def create_stapled_memory_object_stream(max_buffer_size: float = 0) -> MemoryStapledObjectStream:
    return MemoryStapledObjectStream(*anyio.create_memory_object_stream(max_buffer_size))


# FIXME: https://github.com/python/mypy/issues/15238
# FIXME: https://youtrack.jetbrains.com/issues?q=tag:%20%7BPEP%20695%7D
def create_memory_object_stream[T](max_buffer_size: float = 0) -> tuple[
    MemoryObjectSendStream[T],
    MemoryObjectReceiveStream[T],
]:
    return anyio.create_memory_object_stream[T](max_buffer_size)  # noqa


def staple_memory_object_stream(
        *args: anyio.create_memory_object_stream[T],
) -> MemoryStapledObjectStream[T]:
    send, receive = args
    return MemoryStapledObjectStream(
        check.isinstance(send, MemoryObjectSendStream),  # type: ignore
        check.isinstance(receive, MemoryObjectReceiveStream),  # type: ignore
    )


# FIXME: https://github.com/python/mypy/issues/15238
# FIXME: https://youtrack.jetbrains.com/issues?q=tag:%20%7BPEP%20695%7D
def staple_memory_object_stream2[T](max_buffer_size: float = 0) -> MemoryStapledObjectStream[T]:
    send, receive = anyio.create_memory_object_stream[T](max_buffer_size)
    return MemoryStapledObjectStream(
        check.isinstance(send, MemoryObjectSendStream),  # type: ignore
        check.isinstance(receive, MemoryObjectReceiveStream),  # type: ignore
    )


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


##


async def install_shutdown_signal_handler(
        tg: anyio.abc.TaskGroup,
        event: anyio.Event | None = None,
        *,
        signals: ta.Iterable[int] = (signal.SIGINT, signal.SIGTERM),
        echo: bool = False,
) -> ta.Callable[..., ta.Awaitable[None]] | None:
    if event is None:
        event = anyio.Event()

    async def _handler(*, task_status=anyio.TASK_STATUS_IGNORED):
        with anyio.open_signal_receiver(*signals) as it:  # type: ignore
            task_status.started()
            async for signum in it:
                if echo:
                    if signum == signal.SIGINT:
                        print('Ctrl+C pressed!')
                    else:
                        print('Terminated!')
                event.set()
                return

    await tg.start(_handler)
    return event.wait
