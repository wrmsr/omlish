import collections
import typing as ta


T = ta.TypeVar('T')


##


_MISSING = object()


class PeekIterator(ta.Iterator[T]):
    def __init__(self, it: ta.Iterable[T]) -> None:
        super().__init__()

        self._it = iter(it)
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
