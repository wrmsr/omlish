import abc
import typing as ta

from omlish import dataclasses as dc
from omlish import lang

from .similarity import Similarity
from .vectors import Vector


##


@dc.dataclass(frozen=True)
class Indexed(lang.Final):
    v: ta.Any
    vec: Vector


@dc.dataclass(frozen=True)
class Search(lang.Final):
    vec: Vector

    _: dc.KW_ONLY

    k: int = 10
    similarity: Similarity = Similarity.DOT


@dc.dataclass(frozen=True)
class Hit(lang.Final):
    v: ta.Any
    score: float


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
