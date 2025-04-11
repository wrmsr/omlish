import typing as ta

from omlish import check


K = ta.TypeVar('K')
V = ta.TypeVar('V')


##


class SealableRegistry(ta.Generic[K, V]):
    def __init__(self) -> None:
        super().__init__()

        self._dct: dict[K, V] = {}
        self._sealed = False

    def seal(self) -> None:
        self._sealed = True

    def __setitem__(self, k: K, v: V) -> None:
        check.state(not self._sealed)
        check.not_in(k, self._dct)
        self._dct[k] = v

    def __getitem__(self, k: K) -> V:
        self.seal()
        return self._dct[k]

    def items(self) -> ta.Iterator[tuple[K, V]]:
        self.seal()
        return iter(self._dct.items())
