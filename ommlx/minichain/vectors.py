import abc
import typing as ta

from omlish import dataclasses as dc
from omlish import lang


##


@dc.dataclass(frozen=True)
class Vector:
    """array.array('f' | 'd', ...) preferred"""

    v: ta.Sequence[float]


##


@dc.dataclass(frozen=True)
class Indexed(lang.Final):
    vec: Vector
    v: ta.Any


@dc.dataclass(frozen=True)
class Search(lang.Final):
    vec: Vector
    k: int = 10


@dc.dataclass(frozen=True)
class Hit(lang.Final):
    score: float
    v: ta.Any


@dc.dataclass(frozen=True)
class Hits(lang.Final):
    l: ta.Sequence[Hit]


class VectorStore(lang.Abstract):
    @abc.abstractmethod
    def index(self, doc: Indexed) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def search(self, search: Search) -> Hits:
        raise NotImplementedError
