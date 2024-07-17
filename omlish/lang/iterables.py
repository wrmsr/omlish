import itertools
import typing as ta


T = ta.TypeVar('T')


BUILTIN_SCALAR_ITERABLE_TYPES: tuple[type, ...] = (
    bytearray,
    bytes,
    str,
)


def ilen(it: ta.Iterable) -> int:
    c = 0
    for _ in it:
        c += 1
    return c


def take(n: int, it: ta.Iterable[T]) -> list[T]:
    return list(itertools.islice(it, n))


def exhaust(it: ta.Iterable[ta.Any]) -> None:
    for _ in it:
        pass


def peek(vs: ta.Iterable[T]) -> tuple[T, ta.Iterator[T]]:
    it = iter(vs)
    v = next(it)
    return v, itertools.chain(iter((v,)), it)


Rangeable: ta.TypeAlias = int | tuple[int] | tuple[int, int] | ta.Iterable[int]


def asrange(i: Rangeable) -> ta.Iterable[int]:
    if isinstance(i, int):
        return range(i)
    elif isinstance(i, tuple):
        return range(*i)
    elif isinstance(i, ta.Iterable):
        return i
    else:
        raise TypeError(i)


def prodrange(*dims: Rangeable) -> ta.Iterable[ta.Sequence[int]]:
    if not dims:
        return []
    return itertools.product(*map(asrange, dims))
