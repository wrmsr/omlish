import abc
import contextlib
import typing as ta

from ... import lang
from .base import Kv
from .wrappers import underlying_of


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
