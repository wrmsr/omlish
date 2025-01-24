import functools
import heapq
import itertools
import typing as ta

from .iterators import PeekIterator
from .iterators import PrefetchIterator


T = ta.TypeVar('T')
U = ta.TypeVar('U')


def unzip(it: ta.Iterable[T], width: int | None = None) -> list:
    if width is None:
        if not isinstance(it, PeekIterator):
            it = PeekIterator(iter(it))
        try:
            width = len(it.peek())
        except StopIteration:
            return []

    its: list[PrefetchIterator[T]] = []
    running = True

    def next_fn(idx):
        nonlocal running
        if not running:
            raise StopIteration
        try:
            items = next(it)  # type: ignore
        except StopIteration:
            running = False
            raise
        for item_idx, item in enumerate(items):
            its[item_idx].push(item)
        return next(its[idx])

    its.extend(PrefetchIterator(functools.partial(next_fn, idx)) for idx in range(width))
    return its


def take(n: int, iterable: ta.Iterable[T]) -> list[T]:
    return list(itertools.islice(iterable, n))


def chunk(n: int, iterable: ta.Iterable[T], strict: bool = False) -> ta.Iterator[list[T]]:
    # TODO: remove with 3.13 - 3.12 doesn't support strict
    iterator = iter(functools.partial(take, n, iter(iterable)), [])
    if strict:
        def ret():
            for chunk in iterator:
                if len(chunk) != n:
                    raise ValueError('iterable is not divisible by n.')
                yield chunk
        return iter(ret())
    else:
        return iterator


def merge_on(
        function: ta.Callable[[T], U],
        *its: ta.Iterable[T],
) -> ta.Iterator[tuple[U, list[tuple[int, T]]]]:
    indexed_its = [
        (
            (function(item), it_idx, item)
            for it_idx, item in zip(itertools.repeat(it_idx), it)
        )
        for it_idx, it in enumerate(its)
    ]

    grouped_indexed_its = itertools.groupby(
        heapq.merge(*indexed_its),
        key=lambda item_tuple: item_tuple[0],
    )

    return (
        (fn_item, [(it_idx, item) for _, it_idx, item in grp])
        for fn_item, grp in grouped_indexed_its
    )


def expand_indexed_pairs(
        seq: ta.Iterable[tuple[int, T]],
        default: T,
        *,
        width: int | None = None,
) -> list[T]:
    width_ = width
    if width_ is None:
        width_ = (max(idx for idx, _ in seq) + 1) if seq else 0
    result = [default] * width_
    for idx, value in seq:
        if idx < width_:
            result[idx] = value
    return result
