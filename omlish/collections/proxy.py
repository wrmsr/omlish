import typing as ta

from .. import lang


T = ta.TypeVar('T')
K = ta.TypeVar('K')
V = ta.TypeVar('V')


##


class Proxy(lang.Abstract):
    pass


class ProxySequence(ta.Sequence[T], Proxy):
    def __init__(self, target: ta.Sequence[T]) -> None:
        super().__init__()

        if target is None:
            raise TypeError(target)
        self._target = target

    def __repr__(self) -> str:
        return f'{type(self).__name__}({self._target!r})'

    def __contains__(self, x: ta.Any) -> bool:
        return x in self._target

    def __eq__(self, o: object) -> bool:
        return self._target == o

    def __ge__(self, other: ta.Any) -> bool:
        return self._target >= other

    def __getitem__(self, i: int | slice) -> T:  # type: ignore
        return self._target[i]  # type: ignore

    def __gt__(self, other: ta.Any) -> bool:
        return self._target > other

    def __hash__(self) -> int:
        return hash(self._target)

    def __iter__(self) -> ta.Iterator[T]:
        return iter(self._target)

    def __le__(self, other: ta.Any) -> bool:
        return self._target <= other

    def __len__(self) -> int:
        return len(self._target)

    def __lt__(self, other: ta.Any) -> bool:
        return self._target < other

    def __ne__(self, o: object) -> bool:
        return self._target != o

    def __reversed__(self) -> ta.Iterator[T]:
        return reversed(self._target)

    def count(self, x: ta.Any) -> int:
        return self._target.count(x)

    def index(self, x: ta.Any, *args, **kwargs) -> int:
        return self._target.index(x, *args, **kwargs)


class ProxySet(ta.AbstractSet[T], Proxy):
    def __init__(self, target: ta.AbstractSet[T]) -> None:
        super().__init__()

        if target is None:
            raise TypeError(target)
        self._target = target

    def __repr__(self) -> str:
        return f'{type(self).__name__}({self._target!r})'

    def __and__(self, s: ta.AbstractSet[ta.Any]) -> ta.AbstractSet[T]:
        return self._target & s

    def __contains__(self, x: ta.Any) -> bool:
        return x in self._target

    def __eq__(self, o: object) -> bool:
        return self._target == o

    def __ge__(self, s: ta.AbstractSet[ta.Any]) -> bool:
        return self._target >= s

    def __gt__(self, s: ta.AbstractSet[ta.Any]) -> bool:
        return self._target > s

    def __hash__(self) -> int:
        return hash(self._target)

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


class ProxyMapping(ta.Mapping[K, V], Proxy):
    def __init__(self, target: ta.Mapping[K, V]) -> None:
        super().__init__()

        if target is None:
            raise TypeError(target)
        self._target = target

    def __repr__(self) -> str:
        return f'{type(self).__name__}({self._target!r})'

    def __contains__(self, o: ta.Any) -> bool:
        return o in self._target

    def __eq__(self, o: object) -> bool:
        return self._target == o

    def __ge__(self, other: ta.Any) -> bool:
        return self._target >= other

    def __getitem__(self, k: K) -> V:
        return self._target[k]

    def __gt__(self, other: ta.Any) -> bool:
        return self._target > other

    def __hash__(self) -> int:
        return hash(self._target)

    def __iter__(self) -> ta.Iterator[T]:
        return iter(self._target)  # type: ignore

    def __le__(self, other: ta.Any) -> bool:
        return self._target <= other

    def __len__(self) -> int:
        return len(self._target)

    def __lt__(self, other: ta.Any) -> bool:
        return self._target < other

    def __ne__(self, o: object) -> bool:
        return self._target != o

    @ta.overload
    def get(self, key: K, /) -> V | None: ...

    @ta.overload
    def get(self, key: K, default: V, /) -> V: ...  # noqa

    @ta.overload
    def get(self, key: K, default: T, /) -> V | T: ...  # noqa

    def get(self, key, default=None):
        return self._target.get(key, default)

    def items(self) -> ta.ItemsView[K, V]:
        return self._target.items()

    def keys(self) -> ta.KeysView[K]:
        return self._target.keys()

    def values(self) -> ta.ValuesView[V]:
        return self._target.values()
