import abc
import typing as ta

from omlish import lang

from .interfaces import Kv


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
