import typing as ta


T = ta.TypeVar('T')


class OrderedSet(ta.MutableSet[T]):

    def __init__(self, iterable: ta.Optional[ta.Iterable[T]] = None) -> None:
        super().__init__()
        self._dct: dict[T, ta.Any] = {}
        if iterable is not None:
            self |= iterable  # type: ignore  # noqa

    def __len__(self) -> int:
        return len(self._dct)

    def __contains__(self, item: ta.Any) -> bool:
        return item in self._dct

    def add(self, item: T) -> None:
        if item not in self._dct:
            self._dct[item] = None

    def update(self, items: ta.Iterable[T]) -> None:
        for item in items:
            if item not in self._dct:
                self._dct[item] = None

    def discard(self, item: T) -> None:
        if item in self._dct:
            del self._dct[item]

    def __iter__(self) -> ta.Iterator[T]:
        return iter(self._dct.keys())

    def __reversed__(self):
        return reversed(self._dct.keys())

    def pop(self, last=True):
        if not self:
            raise KeyError('set is empty')
        item = next(reversed(self._dct.keys()))
        self.discard(item)
        return item

    def __repr__(self):
        if not self:
            return '%s()' % (self.__class__.__name__,)
        return '%s(%r)' % (self.__class__.__name__, list(self))

    def __eq__(self, other) -> bool:
        if isinstance(other, OrderedSet):
            return len(self) == len(other) and list(self) == list(other)
        return set(self) == set(other)


class OrderedFrozenSet(ta.FrozenSet[T]):

    _list: ta.Sequence[T]

    def __new__(cls, items: ta.Iterable[T]) -> ta.FrozenSet[T]:  # type: ignore
        item_set = set()
        item_list = []
        for item in items:
            if item not in item_set:
                item_set.add(item)
                item_list.append(item)
        obj = super(cls, OrderedFrozenSet).__new__(cls, item_set)
        obj._list = item_list  # type: ignore  # noqa
        return obj

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}([{", ".join(map(repr, self))}])'

    def __iter__(self) -> ta.Iterator[T]:
        return iter(self._list)

    def __sub__(self, other: ta.Iterable[T]) -> ta.FrozenSet[T]:
        s = set(other)
        return type(self)(i for i in self if i not in s)
