import itertools
import typing as ta


T = ta.TypeVar('T')


def len(it: ta.Iterable) -> int:
    c = 0
    for _ in it:
        c += 1
    return c


def take(n: int, it: ta.Iterable[T]) -> list[T]:
    return list(itertools.islice(it, n))
