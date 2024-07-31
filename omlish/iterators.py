import collections
import functools
import heapq
import itertools
import typing as ta


T = ta.TypeVar('T')
U = ta.TypeVar('U')

_MISSING = object()


class PeekIterator(ta.Iterator[T]):

    def __init__(self, it: ta.Iterator[T]) -> None:
        super().__init__()

        self._it = it
        self._pos = -1
        self._next_item: ta.Any = _MISSING

    _item: T

    def __iter__(self) -> ta.Self:
        return self

    @property
    def done(self) -> bool:
        try:
            self.peek()
        except StopIteration:
            return True
        else:
            return False

    def __next__(self) -> T:
        if self._next_item is not _MISSING:
            self._item = ta.cast(T, self._next_item)
            self._next_item = _MISSING
        else:
            self._item = next(self._it)
        self._pos += 1
        return self._item

    def peek(self) -> T:
        if self._next_item is not _MISSING:
            return ta.cast(T, self._next_item)
        self._next_item = next(self._it)
        return self._next_item

    def next_peek(self) -> T:
        next(self)
        return self.peek()

    def takewhile(self, fn: ta.Callable[[T], bool]) -> ta.Iterator[T]:
        while fn(self.peek()):
            yield next(self)

    def skipwhile(self, fn: ta.Callable[[T], bool]) -> None:
        while fn(self.peek()):
            next(self)

    def takeuntil(self, fn: ta.Callable[[T], bool]) -> ta.Iterator[T]:
        return self.takewhile(lambda e: not fn(e))

    def skipuntil(self, fn: ta.Callable[[T], bool]) -> None:
        self.skipwhile(lambda e: not fn(e))

    def takethrough(self, pos: int) -> ta.Iterator[T]:
        return self.takewhile(lambda _: self._pos < pos)

    def skipthrough(self, pos: int) -> None:
        self.skipwhile(lambda _: self._pos < pos)

    def taketo(self, pos: int) -> ta.Iterator[T]:
        return self.takethrough(pos - 1)

    def skipto(self, pos: int) -> None:
        self.skipthrough(pos - 1)


class ProxyIterator(ta.Iterator[T]):

    def __init__(self, fn: ta.Callable[[], T]) -> None:
        self._fn = fn

    def __iter__(self) -> ta.Self:
        return self

    def __next__(self) -> T:
        return self._fn()


class PrefetchIterator(ta.Iterator[T]):

    def __init__(self, fn: ta.Callable[[], T] | None = None) -> None:
        super().__init__()

        self._fn = fn
        self._deque: collections.deque[T] = collections.deque()

    def __iter__(self) -> ta.Self:
        return self

    def push(self, item) -> None:
        self._deque.append(item)

    def __next__(self) -> T:
        try:
            return self._deque.popleft()
        except IndexError:
            if self._fn is None:
                raise StopIteration from None
        return self._fn()


class RetainIterator(ta.Iterator[T]):

    def __init__(self, fn: ta.Callable[[], T]) -> None:
        super().__init__()

        self._fn = fn
        self._deque: collections.deque[T] = collections.deque()

    def __iter__(self) -> ta.Self:
        return self

    def pop(self) -> None:
        self._deque.popleft()

    def __next__(self) -> T:
        item = self._fn()
        self._deque.append(item)
        return item


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


##
# https://docs.python.org/3/library/itertools.html#itertools-recipes


def sliding_window(it: ta.Iterable[T], n: int) -> ta.Iterator[tuple[T, ...]]:
    # sliding_window('ABCDEFG', 4) -> ABCD BCDE CDEF DEFG
    iterator = iter(it)
    window = collections.deque(itertools.islice(iterator, n - 1), maxlen=n)
    for x in iterator:
        window.append(x)
        yield tuple(window)
