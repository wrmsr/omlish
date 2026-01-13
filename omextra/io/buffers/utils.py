# ruff: noqa: UP006 UP045
# @omlish-lite
import typing as ta


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


def can_bytes(obg: ta.Any) -> bool:
    return isinstance(obg, (bytes, bytearray, memoryview)) or hasattr(obg, 'segments')


def iter_bytes_segments(obg: ta.Any) -> ta.Iterator[memoryview]:
    if isinstance(obg, memoryview):
        yield obg
    elif isinstance(obg, (bytes, bytearray)):
        yield memoryview(obg)
    elif hasattr(obg, 'segments'):
        yield from ta.cast('ta.Iterable[memoryview]', obg.segments())
    else:
        raise TypeError(obg)


def to_bytes(obg: ta.Any) -> bytes:
    if isinstance(obg, bytes):
        return obg
    elif isinstance(obg, bytearray):
        return bytes(obg)
    elif isinstance(obg, memoryview):
        return obg.tobytes()
    elif hasattr(obg, 'tobytes'):
        return ta.cast(bytes, obg.tobytes())
    elif hasattr(obg, 'segments'):
        return b''.join(bytes(mv) for mv in obg.segments())
    else:
        raise TypeError(obg)


def bytes_len(obg: ta.Any) -> int:
    if isinstance(obg, (bytes, bytearray, memoryview)):
        return len(obg)
    elif hasattr(obg, 'segments'):
        return sum(len(mv) for mv in obg.segments())
    else:
        # Not bytes-like
        return 0
