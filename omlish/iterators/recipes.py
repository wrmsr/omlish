"""
https://docs.python.org/3/library/itertools.html#itertools-recipes
"""
import collections
import itertools
import typing as ta


T = ta.TypeVar('T')


##


def sliding_window(it: ta.Iterable[T], n: int) -> ta.Iterator[tuple[T, ...]]:
    # sliding_window('ABCDEFG', 4) -> ABCD BCDE CDEF DEFG
    iterator = iter(it)
    window = collections.deque(itertools.islice(iterator, n - 1), maxlen=n)
    for x in iterator:
        window.append(x)
        yield tuple(window)
