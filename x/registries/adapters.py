import typing as ta

from omlish import lang

from .base import Registry


K = ta.TypeVar('K')
V = ta.TypeVar('V')


##


class RegistryMapping(lang.Abstract, ta.Generic[K, V]):  # noqa
    def __init__(self, reg: Registry[K, V]) -> None:
        super().__init__()

        self._reg = reg

    def __len__(self) -> int:
        i = 0
        for _ in self:
            i += 1
        return i

    def __iter__(self) -> ta.Iterator[K]:
        s = set()
        for k, _ in self._reg:
            if k not in s:
                s.add(k)
                yield k


class MultiRegistryMapping(RegistryMapping[K, V], ta.Mapping[K, ta.Sequence[V]]):
    def __getitem__(self, key: K, /) -> ta.Sequence[V]:
        l = [x.v for x in self._reg[key]]
        if not l:
            raise KeyError(key)
        return l


class UniqueRegistryMapping(RegistryMapping[K, V], ta.Mapping[K, V]):
    def __getitem__(self, key: K, /) -> V:
        [x] = self._reg[key]
        return x.v
