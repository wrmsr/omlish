import abc

from omlish import lang

from .base import Kv
from .wrappers import underlying_of


##


class Flushable(lang.Abstract):
    @abc.abstractmethod
    def flush(self) -> None:
        raise NotImplementedError


def flush(root: Kv) -> None:
    for c in underlying_of(root, Flushable):  # type: ignore[type-abstract]
        c.flush()
