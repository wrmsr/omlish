import typing as ta

from omlish import lang

from .base import Kv
from .wrappers import SimpleWrapperKv


K = ta.TypeVar('K')
V = ta.TypeVar('V')


##


class KeyFilteredKv(SimpleWrapperKv[K, V]):
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


#


class ValueFilteredKv(SimpleWrapperKv[K, V]):
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
            raise KeyError(k)
        return v

    def __len__(self) -> int:
        return lang.ilen(self.items())

    def items(self) -> ta.Iterator[tuple[K, V]]:
        fn = self._fn
        return filter(lambda t: fn(t[1]), self._u.items())
