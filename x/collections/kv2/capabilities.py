import abc
import contextlib
import typing as ta

from omlish import lang

from .interfaces import Kv
from .wrappers import underlying_of


K = ta.TypeVar('K')
V = ta.TypeVar('V')
KvT = ta.TypeVar('KvT', bound=Kv)


##


class Closeable(lang.Abstract):
    @abc.abstractmethod
    def close(self) -> None:
        pass


def close(root: Kv) -> None:
    for c in underlying_of(root, Closeable):  # type: ignore[type-abstract]
        c.close()


@contextlib.contextmanager
def closing(kv: KvT) -> ta.Iterator[KvT]:
    try:
        yield kv
    finally:
        close(kv)


##


class Flushable(lang.Abstract):
    @abc.abstractmethod
    def flush(self) -> None:
        pass


def flush(root: Kv) -> None:
    for c in underlying_of(root, Flushable):  # type: ignore[type-abstract]
        c.flush()


##


class Container(lang.Abstract, ta.Generic[K]):
    @abc.abstractmethod
    def __contains__(self, k: K) -> bool:
        raise NotImplementedError


def contains(kv: Kv[K, V], k: K) -> bool:
    # FIXME: not propagated / shrinkwrapped
    if isinstance(kv, Container):
        return k in kv

    try:
        # FIXME: specifically just Queryable
        kv[k]  # noqa
    except KeyError:
        return False
    else:
        return True
