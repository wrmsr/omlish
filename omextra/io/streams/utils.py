# ruff: noqa: UP006 UP045
# @omlish-lite
import typing as ta

from .types import ByteStreamBufferLike
from .types import ByteStreamBufferView


##


def _norm_slice(length: int, start: int, end: ta.Optional[int]) -> ta.Tuple[int, int]:
    if start < 0:
        start += length
    if start < 0:
        start = 0
    if start > length:
        start = length

    if end is None:
        end = length
    else:
        if end < 0:
            end += length
        if end < 0:
            end = 0
        if end > length:
            end = length

    if end < start:
        end = start

    return start, end


##


def can_bytes(obj: ta.Any) -> bool:
    return isinstance(obj, (bytes, bytearray, memoryview, ByteStreamBufferLike))


def iter_bytes_segments(obj: ta.Any) -> ta.Iterator[memoryview]:
    if isinstance(obj, memoryview):
        yield obj
    elif isinstance(obj, (bytes, bytearray)):
        yield memoryview(obj)
    elif isinstance(obj, ByteStreamBufferLike):
        yield from obj.segments()
    else:
        raise TypeError(obj)


def to_bytes(obj: ta.Any) -> bytes:
    if isinstance(obj, bytes):
        return obj
    elif isinstance(obj, bytearray):
        return bytes(obj)
    elif isinstance(obj, memoryview):
        return obj.tobytes()
    elif isinstance(obj, ByteStreamBufferView):
        return obj.tobytes()
    elif isinstance(obj, ByteStreamBufferLike):
        return b''.join(bytes(mv) for mv in obj.segments())
    else:
        raise TypeError(obj)


def bytes_len(obj: ta.Any) -> int:
    if isinstance(obj, (bytes, bytearray, memoryview)):
        return len(obj)
    elif isinstance(obj, ByteStreamBufferLike):
        return sum(len(mv) for mv in obj.segments())
    else:
        # Not bytes-like
        return 0
