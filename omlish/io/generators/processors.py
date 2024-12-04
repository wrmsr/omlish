import typing as ta

from .stepped import flatmap_stepped_generator


T = ta.TypeVar('T')
R = ta.TypeVar('R')


##


def _join_bytes(l: ta.Sequence[bytes]) -> bytes:
    if not l:
        return b''
    elif len(l) == 1:
        return l[0]
    else:
        return b''.join(l)


def _join_str(l: ta.Sequence[str]) -> str:
    if not l:
        return ''
    elif len(l) == 1:
        return l[0]
    else:
        return ''.join(l)


def _is_empty(o: T) -> bool:
    return len(o) < 1  # type: ignore


##


def joined_bytes_generator_processor(
        g: ta.Generator[bytes | None, bytes | None, R],
) -> ta.Generator[bytes, bytes, R]:
    return flatmap_stepped_generator(_join_bytes, g, terminate=_is_empty)


def joined_str_generator_processor(
        g: ta.Generator[str | None, str | None, R],
) -> ta.Generator[str, str, R]:
    return flatmap_stepped_generator(_join_str, g, terminate=_is_empty)
