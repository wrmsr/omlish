import typing as ta

from .base import Registry
from .base import RegistryLookup


K = ta.TypeVar('K')
V = ta.TypeVar('V')


##


class MultiDictRegistry(Registry[K, V]):
    def __init__(self, dct: ta.Mapping[K, ta.Sequence[V]]) -> None:
        super().__init__()

        self._dct = dct

    @classmethod
    def of_tuples(cls, tups: ta.Iterable[tuple[K, V]]) -> 'MultiDictRegistry[K, V]':
        dct: dict[K, list[V]] = {}
        for k, v in tups:
            try:
                l = dct[k]
            except KeyError:
                l = dct[k] = []
            l.append(v)
        return cls(dct)

    def __getitem__(self, k: K, /) -> ta.Iterator[RegistryLookup[K, V]]:
        for v in self._dct.get(k, []):
            yield RegistryLookup(v, self)

    def __iter__(self) -> ta.Iterator[tuple[K, RegistryLookup[K, V]]]:
        for k, vs in self._dct.items():
            for v in vs:
                yield (k, RegistryLookup(v, self))


class UniqueDictRegistry(Registry[K, V]):
    def __init__(self, dct: ta.Mapping[K, V]) -> None:
        super().__init__()

        self._dct = dct

    def __getitem__(self, k: K, /) -> ta.Iterator[RegistryLookup[K, V]]:
        try:
            v = self._dct[k]
        except KeyError:
            return
        yield RegistryLookup(v, self)

    def __iter__(self) -> ta.Iterator[tuple[K, RegistryLookup[K, V]]]:
        for k, v in self._dct.items():
            yield (k, RegistryLookup(v, self))
