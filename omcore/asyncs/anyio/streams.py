import dataclasses as dc
import typing as ta

import anyio.streams.memory
import anyio.streams.stapled

from ... import check


T = ta.TypeVar('T')


##


MemoryObjectReceiveStream: ta.TypeAlias = anyio.streams.memory.MemoryObjectReceiveStream
MemoryObjectSendStream: ta.TypeAlias = anyio.streams.memory.MemoryObjectSendStream

StapledByteStream: ta.TypeAlias = anyio.streams.stapled.StapledByteStream
StapledObjectStream: ta.TypeAlias = anyio.streams.stapled.StapledObjectStream


@dc.dataclass(eq=False)
class MemoryStapledObjectStream(StapledObjectStream[T]):
    send_stream: MemoryObjectSendStream[T]
    receive_stream: MemoryObjectReceiveStream[T]


def split_memory_object_streams(
        *args: anyio.create_memory_object_stream[T],
) -> tuple[
    MemoryObjectSendStream[T],
    MemoryObjectReceiveStream[T],
]:
    [tup] = args
    return tup  # noqa


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
        check.isinstance(send, MemoryObjectSendStream),
        check.isinstance(receive, MemoryObjectReceiveStream),
    )


# FIXME: https://github.com/python/mypy/issues/15238
# FIXME: https://youtrack.jetbrains.com/issues?q=tag:%20%7BPEP%20695%7D
def staple_memory_object_stream2[T](max_buffer_size: float = 0) -> MemoryStapledObjectStream[T]:
    send, receive = anyio.create_memory_object_stream[T](max_buffer_size)
    return MemoryStapledObjectStream(
        check.isinstance(send, MemoryObjectSendStream),
        check.isinstance(receive, MemoryObjectReceiveStream),
    )
