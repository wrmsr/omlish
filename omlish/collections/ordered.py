import typing as ta


T = ta.TypeVar('T')


##


class OrderedSet(ta.MutableSet[T]):
    def __init__(self, iterable: ta.Iterable[T] | None = None) -> None:
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

    def pop(self, last: bool = True) -> T:
        if not self:
            raise KeyError('set is empty')
        item = next(reversed(self._dct.keys()))
        self.discard(item)
        return item

    def __repr__(self) -> str:
        if not self:
            return f'{self.__class__.__name__}()'
        return f'{self.__class__.__name__}({list(self)!r})'

    def __eq__(self, other) -> bool:
        if isinstance(other, OrderedSet):
            return len(self) == len(other) and list(self) == list(other)
        return set(self) == set(other)

    def __ne__(self, other) -> bool:
        return not (self == other)

    def __hash__(self) -> int:
        raise TypeError


class OrderedFrozenSet(ta.FrozenSet[T]):  # noqa
    _list: ta.Sequence[T]

    def __new__(cls, items: ta.Iterable[T]) -> frozenset[T]:  # type: ignore
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

    def __sub__(self, other: ta.Iterable[T]) -> frozenset[T]:
        s = set(other)
        return type(self)(i for i in self if i not in s)
