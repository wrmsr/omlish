import typing as ta

from omlish import lang

from .base import Registry
from .base import RegistryLookup
from .base import DuplicateKeyRegisteredError


K = ta.TypeVar('K')
V = ta.TypeVar('V')
T = ta.TypeVar('T')


##


class CompositeRegistry(Registry[K, V], lang.Abstract):  # noqa
    def __init__(self, *children: Registry[K, V]) -> None:
        super().__init__()

        self._children = children

    @property
    def children(self) -> ta.Sequence[Registry[K, V]]:
        return self._children


class AllCompositeRegistry(CompositeRegistry[K, V]):
    def __getitem__(self, k: K, /) -> ta.Iterator[RegistryLookup[K, V]]:
        for c in self._children:
            for x in c[k]:
                yield x

    def __iter__(self) -> ta.Iterator[tuple[K, RegistryLookup[K, V]]]:
        for c in self._children:
            yield from c


class FirstCompositeRegistry(CompositeRegistry[K, V]):
    def __getitem__(self, k: K, /) -> ta.Iterator[RegistryLookup[K, V]]:
        for c in self._children:
            i = 0
            for i, x in enumerate(c[k]):
                yield x
            if i:
                break

    def __iter__(self) -> ta.Iterator[tuple[K, RegistryLookup[K, V]]]:
        s = set()
        for c in self._children:
            cs = set()
            for k, x in c:
                if k in s:
                    continue
                cs.add(k)
                yield (k, x)
            s.update(cs)


class UniqueCompositeRegistry(CompositeRegistry[K, V]):
    def __getitem__(self, k: K, /) -> ta.Iterator[RegistryLookup[K, V]]:
        r: ta.Any = self._NOT_SET
        for c in self._children:
            for x in c[k]:
                if r is self._NOT_SET:
                    r = x
                else:
                    raise DuplicateKeyRegisteredError(k, (x, r))
        if r is not self._NOT_SET:
            yield r

    def __iter__(self) -> ta.Iterator[tuple[K, RegistryLookup[K, V]]]:
        dct: dict[K, RegistryLookup[K, V]] = {}
        for c in self._children:
            for k, x in c:
                if k in dct:
                    raise DuplicateKeyRegisteredError(k, (dct[k], x))
                yield (k, x)
