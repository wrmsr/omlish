import typing as ta

from omlish import lang

from .interfaces import Kv
from .shrinkwraps import ShrinkwrapFullKv


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

    def __setitem__(self, k: K, v: V, /) -> None:
        if not self._fn(k):
            raise KeyError(k)
        self._u[k] = v

    def __delitem__(self, k: K, /) -> None:
        if not self._fn(k):
            raise KeyError(k)
        del self._u[k]


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

    def __setitem__(self, k: K, v: V, /) -> None:
        if not self._fn(v):
            raise ValueFilteredKeyError(k)
        self._u[k] = v
