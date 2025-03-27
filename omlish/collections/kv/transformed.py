import typing as ta

from ... import check
from .base import Kv
from .base import MutableKv
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


class KeyTransformedMutableKey(KeyTransformedKv[KT, KF, V], MutableKv[KT, V], ta.Generic[KT, KF, V]):
    def __init__(
            self,
            u: MutableKv[KF, V],
            *,
            t_to_f: ta.Callable[[KT], KF] | None = None,
            f_to_t: ta.Callable[[KF], KT] | None = None,
    ) -> None:
        super().__init__(
            u,
            t_to_f=t_to_f,
            f_to_t=f_to_t,
        )

    _u: MutableKv[KF, V]

    def __setitem__(self, k: KT, v: V) -> None:
        fn = check.not_none(self._t_to_f)
        self._u[fn(k)] = v

    def __delitem__(self, k: KT) -> None:
        fn = check.not_none(self._t_to_f)
        del self._u[fn(k)]


##


class ValueTransformedKv(WrapperKv[K, VT], ta.Generic[K, VT, VF]):
    def __init__(
            self,
            u: Kv[K, VF],
            f_to_t: ta.Callable[[VF], VT] | None = None,
    ) -> None:
        super().__init__()

        self._u = u
        self._f_to_t = f_to_t

    def underlying(self) -> ta.Sequence[Kv]:
        return [self._u]

    def __getitem__(self, k: K, /) -> VT:
        fn = check.not_none(self._f_to_t)
        return fn(self._u[k])

    def __len__(self) -> int:
        return len(self._u)

    def items(self) -> ta.Iterator[tuple[K, VT]]:
        fn = check.not_none(self._f_to_t)
        return ((k, fn(v)) for k, v in self._u.items())


class ValueTransformedMutableKv(ValueTransformedKv[K, VT, VF], MutableKv[K, VT], ta.Generic[K, VT, VF]):
    def __init__(
            self,
            u: MutableKv[K, VF],
            *,
            f_to_t: ta.Callable[[VF], VT] | None = None,
            t_to_f: ta.Callable[[VT], VF] | None = None,
    ) -> None:
        super().__init__(u, f_to_t)

        self._t_to_f = t_to_f

    _u: MutableKv[K, VF]

    def __setitem__(self, k: K, v: VT) -> None:
        fn = check.not_none(self._t_to_f)
        self._u[k] = fn(v)

    def __delitem__(self, k: K) -> None:
        del self._u[k]
