import typing as ta

from omlish import lang

from .base import Registry
from .base import RegistryLookup


K = ta.TypeVar('K')
V = ta.TypeVar('V')


##


class WrapperRegistry(Registry[K, V], lang.Abstract):  # noqa
    def __init__(self, child: Registry[K, V]) -> None:
        super().__init__()

        self._child = child

    @property
    def child(self) -> Registry[K, V]:
        return self._child

    @property
    def children(self) -> ta.Sequence[Registry[K, V]]:
        return (self._child,)


##


class CachedRegistry(WrapperRegistry[K, V]):
    def __init__(self, child: Registry[K, V]) -> None:
        super().__init__(child)

        self._dct: dict[K, ta.Sequence[RegistryLookup[K, V]]] = {}

    def invalidate(self) -> None:
        self._dct = {}

    def __getitem__(self, k: K, /) -> ta.Iterator[RegistryLookup[K, V]]:
        try:
            h = self._dct[k]
        except KeyError:
            h = self._dct[k] = list(self._child[k])
        yield from h

    def __iter__(self) -> ta.Iterator[tuple[K, RegistryLookup[K, V]]]:
        return iter(self._child)


##


class LockedRegistry(WrapperRegistry[K, V]):
    def __init__(
            self,
            child: Registry[K, V],
            lock: lang.DefaultLockable = None,
    ) -> None:
        super().__init__(child)

        self._lock = lang.default_lock(lock, True)

    def __getitem__(self, k: K, /) -> ta.Iterator[RegistryLookup[K, V]]:
        with self._lock():
            yield from self._child[k]

    def __iter__(self) -> ta.Iterator[tuple[K, RegistryLookup[K, V]]]:
        with self._lock():
            yield from self._child
