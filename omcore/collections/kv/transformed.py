import typing as ta

from ... import check
from .base import Kv
from .base import MutableKv
from .wrappers import WrapperKv


K = ta.TypeVar('K')
V = ta.TypeVar('V')

# 'Above' the wrapper
KA = ta.TypeVar('KA')
VA = ta.TypeVar('VA')

# 'Below' the wrapper
KB = ta.TypeVar('KB')
VB = ta.TypeVar('VB')


##


class KeyTransformedKv(WrapperKv[KA, V], ta.Generic[KA, KB, V]):
    def __init__(
            self,
            u: Kv[KB, V],
            *,
            a_to_b: ta.Callable[[KA], KB] | None = None,
            b_to_a: ta.Callable[[KB], KA] | None = None,
    ) -> None:
        super().__init__()

        self._u = u
        self._a_to_b = a_to_b
        self._b_to_a = b_to_a

    def underlying(self) -> ta.Sequence[Kv]:
        return [self._u]

    def __getitem__(self, k: KA, /) -> V:
        fn = check.not_none(self._a_to_b)
        return self._u[fn(k)]

    def __len__(self) -> int:
        return len(self._u)

    def items(self) -> ta.Iterator[tuple[KA, V]]:
        fn = check.not_none(self._b_to_a)
        return ((fn(k), v) for k, v in self._u.items())


class KeyTransformedMutableKey(KeyTransformedKv[KA, KB, V], MutableKv[KA, V], ta.Generic[KA, KB, V]):
    def __init__(
            self,
            u: MutableKv[KB, V],
            *,
            a_to_b: ta.Callable[[KA], KB] | None = None,
            b_to_a: ta.Callable[[KB], KA] | None = None,
    ) -> None:
        super().__init__(
            u,
            a_to_b=a_to_b,
            b_to_a=b_to_a,
        )

    _u: MutableKv[KB, V]

    def __setitem__(self, k: KA, v: V, /) -> None:
        fn = check.not_none(self._a_to_b)
        self._u[fn(k)] = v

    def __delitem__(self, k: KA, /) -> None:
        fn = check.not_none(self._a_to_b)
        del self._u[fn(k)]


##


class ValueTransformedKv(WrapperKv[K, VA], ta.Generic[K, VA, VB]):
    def __init__(
            self,
            u: Kv[K, VB],
            b_to_a: ta.Callable[[VB], VA] | None = None,
    ) -> None:
        super().__init__()

        self._u = u
        self._b_to_a = b_to_a

    def underlying(self) -> ta.Sequence[Kv]:
        return [self._u]

    def __getitem__(self, k: K, /) -> VA:
        fn = check.not_none(self._b_to_a)
        return fn(self._u[k])

    def __len__(self) -> int:
        return len(self._u)

    def items(self) -> ta.Iterator[tuple[K, VA]]:
        fn = check.not_none(self._b_to_a)
        return ((k, fn(v)) for k, v in self._u.items())


class ValueTransformedMutableKv(ValueTransformedKv[K, VA, VB], MutableKv[K, VA], ta.Generic[K, VA, VB]):
    def __init__(
            self,
            u: MutableKv[K, VB],
            *,
            b_to_a: ta.Callable[[VB], VA] | None = None,
            a_to_b: ta.Callable[[VA], VB] | None = None,
    ) -> None:
        super().__init__(u, b_to_a)

        self._a_to_b = a_to_b

    _u: MutableKv[K, VB]

    def __setitem__(self, k: K, v: VA, /) -> None:
        fn = check.not_none(self._a_to_b)
        self._u[k] = fn(v)

    def __delitem__(self, k: K, /) -> None:
        del self._u[k]
