import typing as ta

from .. import lang


T = ta.TypeVar('T')
K = ta.TypeVar('K')
V = ta.TypeVar('V')


class Unmodifiable(lang.Abstract):
    pass


class UnmodifiableSequence(ta.Sequence[T], Unmodifiable, lang.Final):

    def __init__(self, target: ta.Sequence[T]) -> None:
        super().__init__()

        if target is None:
            raise TypeError(target)
        self._target = target

    def __repr__(self) -> str:
        return '%s(%r)' % (type(self).__name__, self._target)

    def __contains__(self, x: object) -> bool:
        return x in self._target

    def __eq__(self, o: object) -> bool:
        return self._target == o

    def __ge__(self, other: object) -> bool:
        return self._target >= other  # type: ignore

    def __getitem__(self, i: ta.Union[int, slice]) -> T:  # type: ignore
        return self._target[i]  # type: ignore

    def __gt__(self, other: object) -> bool:
        return self._target > other  # type: ignore

    def __iter__(self) -> ta.Iterator[T]:
        return iter(self._target)

    def __le__(self, other: object) -> bool:
        return self._target <= other  # type: ignore

    def __len__(self) -> int:
        return len(self._target)

    def __lt__(self, other: object) -> bool:
        return self._target < other  # type: ignore

    def __ne__(self, o: object) -> bool:
        return self._target != o

    def __reversed__(self) -> ta.Iterator[T]:
        return reversed(self._target)

    def count(self, x: ta.Any) -> int:
        return self._target.count(x)

    def index(self, x: ta.Any, *args, **kwargs) -> int:  # type: ignore
        return self._target.index(x, *args, **kwargs)


class UnmodifiableSet(ta.AbstractSet[T], Unmodifiable, lang.Final):

    def __init__(self, target: ta.AbstractSet[T]) -> None:
        super().__init__()

        if target is None:
            raise TypeError(target)
        self._target = target

    def __repr__(self) -> str:
        return '%s(%r)' % (type(self).__name__, self._target)

    def __and__(self, s: ta.AbstractSet[ta.Any]) -> ta.AbstractSet[T]:
        return self._target & s

    def __contains__(self, x: object) -> bool:
        return x in self._target

    def __eq__(self, o: object) -> bool:
        return self._target == o

    def __ge__(self, s: ta.AbstractSet[ta.Any]) -> bool:
        return self._target >= s

    def __gt__(self, s: ta.AbstractSet[ta.Any]) -> bool:
        return self._target > s

    def __iter__(self) -> ta.Iterator[T]:
        return iter(self._target)

    def __le__(self, s: ta.AbstractSet[ta.Any]) -> bool:
        return self._target <= s

    def __len__(self) -> int:
        return len(self._target)

    def __lt__(self, s: ta.AbstractSet[ta.Any]) -> bool:
        return self._target > s

    def __ne__(self, o: object) -> bool:
        return self._target != o

    def __or__(self, s: ta.AbstractSet[T]) -> ta.AbstractSet[T]:  # type: ignore
        return self._target | s

    def __sub__(self, s: ta.AbstractSet[ta.Any]) -> ta.AbstractSet[T]:
        return self._target - s

    def __xor__(self, s: ta.AbstractSet[T]) -> ta.AbstractSet[T]:  # type: ignore
        return self._target ^ s

    def isdisjoint(self, s: ta.Iterable[ta.Any]) -> bool:
        return self._target.isdisjoint(s)


class UnmodifiableMapping(ta.Mapping[K, V], Unmodifiable, lang.Final):

    def __init__(self, target: ta.Mapping[K, V]) -> None:
        super().__init__()

        if target is None:
            raise TypeError(target)
        self._target = target

    def __repr__(self) -> str:
        return '%s(%r)' % (type(self).__name__, self._target)

    def __contains__(self, o: object) -> bool:
        return o in self._target

    def __eq__(self, o: object) -> bool:
        return self._target == o

    def __ge__(self, other: object) -> bool:
        return self._target >= other  # type: ignore

    def __getitem__(self, k: K) -> V:
        return self._target[k]

    def __gt__(self, other: object) -> bool:
        return self._target > other  # type: ignore

    def __iter__(self) -> ta.Iterator[T]:
        return iter(self._target)  # type: ignore

    def __le__(self, other: object) -> bool:
        return self._target <= other  # type: ignore

    def __len__(self) -> int:
        return len(self._target)

    def __lt__(self, other: object) -> bool:
        return self._target < other  # type: ignore

    def __ne__(self, o: object) -> bool:
        return self._target != o

    def get(self, k: K, default=None) -> ta.Optional[V]:  # type: ignore
        return self._target.get(k)

    def items(self) -> ta.ItemsView[K, V]:
        return self._target.items()

    def keys(self) -> ta.KeysView[K]:
        return self._target.keys()

    def values(self) -> ta.ValuesView[V]:
        return self._target.values()
