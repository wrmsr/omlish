import abc
import typing as ta

from ... import lang
from .base import Kv
from .base import MutableKv


K = ta.TypeVar('K')
V = ta.TypeVar('V')

T = ta.TypeVar('T')


##


class WrapperKv(Kv[K, V], lang.Abstract):
    @abc.abstractmethod
    def underlying(self) -> ta.Iterable[Kv]:
        raise NotImplementedError


##


def underlying(
        root: Kv,
        *,
        leaves_only: bool = False,
        filter: ta.Callable[[Kv], bool] | None = None,  # noqa
) -> ta.Iterator[Kv]:
    def rec(c):
        if isinstance(c, WrapperKv):
            if not leaves_only:
                yield c
            for n in c.underlying():
                yield from rec(n)
        else:
            yield c

    for u in rec(root):
        if filter is not None and not filter(u):
            continue
        yield u


def underlying_of(root: Kv, cls: type[T]) -> ta.Iterator[T]:
    return underlying(root, filter=lambda c: isinstance(c, cls))  # type: ignore[return-value]


##


class SimpleWrapperKv(WrapperKv[K, V]):
    def __init__(self, u: Kv[K, V]) -> None:
        super().__init__()

        self._u = u

    def underlying(self) -> ta.Sequence[Kv]:
        return [self._u]

    def __getitem__(self, k: K, /) -> V:
        return self._u[k]

    def __len__(self) -> int:
        return len(self._u)

    def items(self) -> ta.Iterator[tuple[K, V]]:
        return self._u.items()


class SimpleWrapperMutableKv(SimpleWrapperKv[K, V], MutableKv[K, V]):
    def __init__(self, u: MutableKv[K, V]) -> None:
        super().__init__(u)

    _u: MutableKv[K, V]

    def __setitem__(self, k: K, v: V, /) -> None:
        self._u[k] = v

    def __delitem__(self, k: K, /) -> None:
        del self._u[k]


##


class UnmodifiableError(Exception):
    pass


class UnmodifiableKv(SimpleWrapperKv[K, V], MutableKv[K, V]):
    def __setitem__(self, k: K, v: V, /) -> None:
        raise UnmodifiableError

    def __delitem__(self, k: K, /) -> None:
        raise UnmodifiableError
