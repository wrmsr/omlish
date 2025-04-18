import typing as ta

from omlish import lang

from .bases import KvToKvFunc
from .interfaces import Kv
from .interfaces import SortDirection
from .shrinkwraps import ShrinkwrapFullKv
from .shrinkwraps import shrinkwrap_factory_


K = ta.TypeVar('K')
V = ta.TypeVar('V')


##


class KeyFilteredKv(ShrinkwrapFullKv[K, V]):
    def __init__(
            self,
            u: Kv[K, V],
            fn: ta.Callable[[K], bool],
    ) -> None:
        super().__init__(u)

        self._fn = fn

    def __getitem__(self, k: K, /) -> V:
        if not self._fn(k):
            raise KeyError(k)
        return self._u[k]

    def __len__(self) -> int:
        return lang.ilen(self.items())

    def items(self) -> ta.Iterator[tuple[K, V]]:
        fn = self._fn
        return filter(lambda t: fn(t[0]), self._u.items())

    def sorted_items(
            self,
            start: lang.Maybe[K] = lang.empty(),
            direction: SortDirection = 'asc',
    ) -> ta.Iterator[tuple[K, V]]:
        fn = self._fn
        return filter(lambda t: fn(t[0]), self._u.sorted_items(start, direction))

    def __setitem__(self, k: K, v: V, /) -> None:
        if not self._fn(k):
            raise KeyError(k)
        self._u[k] = v

    def __delitem__(self, k: K, /) -> None:
        if not self._fn(k):
            raise KeyError(k)
        del self._u[k]


def filter_keys(fn: ta.Callable[[K], bool]) -> KvToKvFunc[K, V]:
    return shrinkwrap_factory_(KeyFilteredKv, fn)


##


class ValueFilteredKeyError(KeyError):
    pass


class ValueFilteredKv(ShrinkwrapFullKv[K, V]):
    def __init__(
            self,
            u: Kv[K, V],
            fn: ta.Callable[[V], bool],
    ) -> None:
        super().__init__(u)

        self._fn = fn

    def __getitem__(self, k: K, /) -> V:
        v = self._u[k]
        if not self._fn(v):
            raise ValueFilteredKeyError(k)
        return v

    def __len__(self) -> int:
        return lang.ilen(self.items())

    def items(self) -> ta.Iterator[tuple[K, V]]:
        fn = self._fn
        return ((k, v) for k, v in self._u.items() if fn(v))

    def sorted_items(
            self,
            start: lang.Maybe[K] = lang.empty(),
            direction: SortDirection = 'asc',
    ) -> ta.Iterator[tuple[K, V]]:
        fn = self._fn
        return ((k, v) for k, v in self._u.sorted_items(start, direction) if fn(v))

    def __setitem__(self, k: K, v: V, /) -> None:
        if not self._fn(v):
            raise ValueFilteredKeyError(k)
        self._u[k] = v


def filter_values(fn: ta.Callable[[V], bool]) -> KvToKvFunc[K, V]:
    return shrinkwrap_factory_(ValueFilteredKv, fn)
