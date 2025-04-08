import typing as ta

from omlish import check

from .bases import FullKv
from .interfaces import Kv
from .bases import KvToKvFunc2
from .shrinkwraps import ShrinkwrapKv2
from .shrinkwraps import shrinkwrap_factory_


K = ta.TypeVar('K')
V = ta.TypeVar('V')

# 'Above' the wrapper
KA = ta.TypeVar('KA')
VA = ta.TypeVar('VA')

# 'Below' the wrapper
KB = ta.TypeVar('KB')
VB = ta.TypeVar('VB')


##


class KeyTransformedKv(ShrinkwrapKv2[KA, V, KB, V], ta.Generic[KA, KB, V]):
    def __init__(
            self,
            u: FullKv[KB, V],
            *,
            a_to_b: ta.Callable[[KA], KB] | None = None,
            b_to_a: ta.Callable[[KB], KA] | None = None,
    ) -> None:
        super().__init__(u)

        self._a_to_b = a_to_b
        self._b_to_a = b_to_a

    _u: FullKv[KB, V]

    def __getitem__(self, k: KA, /) -> V:
        fn = check.not_none(self._a_to_b)
        return self._u[fn(k)]

    def __len__(self) -> int:
        return len(self._u)

    def items(self) -> ta.Iterator[tuple[KA, V]]:
        fn = check.not_none(self._b_to_a)
        return ((fn(k), v) for k, v in self._u.items())

    def __setitem__(self, k: KA, v: V, /) -> None:
        fn = check.not_none(self._a_to_b)
        self._u[fn(k)] = v

    def __delitem__(self, k: KA, /) -> None:
        fn = check.not_none(self._a_to_b)
        del self._u[fn(k)]


def transform_keys(
        *,
        a_to_b: ta.Callable[[KA], KB] | None = None,
        b_to_a: ta.Callable[[KB], KA] | None = None,
) -> KvToKvFunc2[KA, V, KB, V]:
    return shrinkwrap_factory_(
        KeyTransformedKv,
        a_to_b=a_to_b,
        b_to_a=b_to_a,
    )


##


class ValueTransformedKv(ShrinkwrapKv2[K, VA, K, VB], ta.Generic[K, VA, VB]):
    def __init__(
            self,
            u: Kv[K, VB],
            *,
            a_to_b: ta.Callable[[VA], VB] | None = None,
            b_to_a: ta.Callable[[VB], VA] | None = None,
    ) -> None:
        super().__init__(u)

        self._a_to_b = a_to_b
        self._b_to_a = b_to_a

    _u: FullKv[K, VB]

    def __getitem__(self, k: K, /) -> VA:
        fn = check.not_none(self._b_to_a)
        return fn(self._u[k])

    def __len__(self) -> int:
        return len(self._u)

    def items(self) -> ta.Iterator[tuple[K, VA]]:
        fn = check.not_none(self._b_to_a)
        return ((k, fn(v)) for k, v in self._u.items())

    def __setitem__(self, k: K, v: VA, /) -> None:
        fn = check.not_none(self._a_to_b)
        self._u[k] = fn(v)

    def __delitem__(self, k: K, /) -> None:
        del self._u[k]


def transform_values(
        *,
        a_to_b: ta.Callable[[VA], VB] | None = None,
        b_to_a: ta.Callable[[VB], VA] | None = None,
) -> KvToKvFunc2[KA, V, KB, V]:
    return shrinkwrap_factory_(
        ValueTransformedKv,
        a_to_b=a_to_b,
        b_to_a=b_to_a,
    )
