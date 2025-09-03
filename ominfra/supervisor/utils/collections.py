# ruff: noqa: UP006 UP007 UP045
import abc
import typing as ta

from omlish.lite.abstract import Abstract


K = ta.TypeVar('K')
V = ta.TypeVar('V')


##


class KeyedCollectionAccessors(Abstract, ta.Generic[K, V]):
    @property
    @abc.abstractmethod
    def _by_key(self) -> ta.Mapping[K, V]:
        raise NotImplementedError

    def __iter__(self) -> ta.Iterator[V]:
        return iter(self._by_key.values())

    def __len__(self) -> int:
        return len(self._by_key)

    def __contains__(self, key: K) -> bool:
        return key in self._by_key

    def __getitem__(self, key: K) -> V:
        return self._by_key[key]

    def get(self, key: K, default: ta.Optional[V] = None) -> ta.Optional[V]:
        return self._by_key.get(key, default)

    def items(self) -> ta.Iterator[ta.Tuple[K, V]]:
        return iter(self._by_key.items())


class KeyedCollection(KeyedCollectionAccessors[K, V], Abstract):
    def __init__(self, items: ta.Iterable[V]) -> None:
        super().__init__()

        by_key: ta.Dict[K, V] = {}
        for v in items:
            if (k := self._key(v)) in by_key:
                raise KeyError(f'key {k} of {v} already registered by {by_key[k]}')
            by_key[k] = v
        self.__by_key = by_key

    @property
    def _by_key(self) -> ta.Mapping[K, V]:
        return self.__by_key

    @abc.abstractmethod
    def _key(self, v: V) -> K:
        raise NotImplementedError
