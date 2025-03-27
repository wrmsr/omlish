import abc
import typing as ta

from omlish import lang

from .base import Kv


K = ta.TypeVar('K')
V = ta.TypeVar('V')

T = ta.TypeVar('T')


##


class WrapperKv(Kv[K, V], lang.Abstract):
    @abc.abstractmethod
    def underlying(self) -> ta.Iterable[Kv]:
        raise NotImplementedError

    def close(self) -> None:
        for u in self.underlying():
            u.close()


##


class SimpleWrapperKv(WrapperKv[K, V], lang.Abstract):
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


##


def underlying(
        root: Kv,
        *,
        leaves_only: bool = False,
        filter: ta.Callable[[Kv], bool] | None = None,  # noqa
) -> ta.Iterator[Kv]:
    def rec(c):
        if c is not root and filter is not None and not filter(c):
            return
        if isinstance(c, WrapperKv):
            if not leaves_only:
                yield c
            for n in c.underlying():
                yield from rec(n)
        else:
            yield c

    yield from rec(root)


def underlying_of(root: Kv, cls: type[T]) -> ta.Iterator[T]:
    return underlying(root, filter=lambda c: isinstance(c, cls))  # type: ignore[return-value]
