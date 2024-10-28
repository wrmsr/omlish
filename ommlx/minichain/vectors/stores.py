import abc
import typing as ta

from omlish import dataclasses as dc
from omlish import lang

from .vectors import Vector


##


@dc.dataclass(frozen=True)
class VectorIndexed(lang.Final):
    v: ta.Any
    vec: Vector


class VectorStore(lang.Abstract):
    @abc.abstractmethod
    def index(self, doc: VectorIndexed) -> None:
        raise NotImplementedError

    # @abc.abstractmethod
    # def search(self, search: VectorSearch) -> VectorHits:
    #     raise NotImplementedError
