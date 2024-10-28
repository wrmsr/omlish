import abc
import typing as ta

from omlish import dataclasses as dc
from omlish import lang

from .similarity import Similarity
from .vectors import Vector


##


@dc.dataclass(frozen=True)
class VectorIndexed(lang.Final):
    v: ta.Any
    vec: Vector


@dc.dataclass(frozen=True)
class VectorSearch(lang.Final):
    vec: Vector

    _: dc.KW_ONLY

    k: int = 10
    similarity: Similarity = Similarity.DOT


@dc.dataclass(frozen=True)
class VectorHit(lang.Final):
    v: ta.Any
    score: float


@dc.dataclass(frozen=True)
class VectorHits(lang.Final):
    l: ta.Sequence[VectorHit]


class VectorStore(lang.Abstract):
    @abc.abstractmethod
    def index(self, doc: VectorIndexed) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def search(self, search: VectorSearch) -> VectorHits:
        raise NotImplementedError
