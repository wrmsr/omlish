import typing as ta

from ... import check
from .base import Kv
from .wrappers import WrapperKv


K = ta.TypeVar('K')
V = ta.TypeVar('V')

KF = ta.TypeVar('KF')
KT = ta.TypeVar('KT')
VF = ta.TypeVar('VF')
VT = ta.TypeVar('VT')


##


class KeyTransformedKv(WrapperKv[KT, V], ta.Generic[KT, KF, V]):
    def __init__(
            self,
            u: Kv[KF, V],
            *,
            t_to_f: ta.Callable[[KT], KF] | None = None,
            f_to_t: ta.Callable[[KF], KT] | None = None,
    ) -> None:
        super().__init__()

        self._u = u
        self._t_to_f = t_to_f
        self._f_to_t = f_to_t

    def underlying(self) -> ta.Sequence[Kv]:
        return [self._u]

    def __getitem__(self, k: KT, /) -> V:
        fn = check.not_none(self._t_to_f)
        return self._u[fn(k)]

    def __len__(self) -> int:
        return len(self._u)

    def items(self) -> ta.Iterator[tuple[KT, V]]:
        fn = check.not_none(self._f_to_t)
        return ((fn(k), v) for k, v in self._u.items())


#


class ValueTransformedKv(WrapperKv[K, VT], ta.Generic[K, VT, VF]):
    def __init__(
            self,
            u: Kv[K, VF],
            fn: ta.Callable[[VF], VT],
    ) -> None:
        super().__init__()

        self._u = u
        self._fn = fn

    def underlying(self) -> ta.Sequence[Kv]:
        return [self._u]

    def __getitem__(self, k: K, /) -> VT:
        return self._fn(self._u[k])

    def __len__(self) -> int:
        return len(self._u)

    def items(self) -> ta.Iterator[tuple[K, VT]]:
        fn = self._fn
        return ((k, fn(v)) for k, v in self._u.items())
