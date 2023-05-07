import collections.abc
import itertools
import typing as ta


T = ta.TypeVar('T')


BUILTIN_SCALAR_ITERABLE_TYPES = {
    bytearray,
    bytes,
    str,
}


def exhaust(it: ta.Iterable[ta.Any]) -> None:
    for _ in it:
        pass


def iterable(obj: T) -> bool:
    return isinstance(obj, collections.abc.Iterable)


def peek(vs: ta.Iterable[T]) -> ta.Tuple[T, ta.Iterator[T]]:
    it = iter(vs)
    v = next(it)
    return v, itertools.chain(iter((v,)), it)


Rangeable = ta.Union[int, ta.Tuple[int], ta.Tuple[int, int], ta.Iterable[int]]


def asrange(i: Rangeable) -> ta.Iterable[int]:
    if isinstance(i, int):
        return range(i)
    elif isinstance(i, tuple):
        return range(*i)
    elif isinstance(i, ta.Iterable):
        return i
    else:
        raise TypeError(i)


def multirange(*dims: Rangeable) -> ta.Iterable[ta.Sequence[int]]:
    if not dims:
        return []
    return itertools.product(*map(asrange, dims))
