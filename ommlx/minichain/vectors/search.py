import abc
import typing as ta

from omlish import dataclasses as dc
from omlish import lang

from ..options import Option
from ..services import Service
from ..services import ServiceOption
from ..services import ServiceRequest
from ..services import ServiceResponse
from .similarity import Similarity
from .vectors import Vector


##


class VectorSearchOption(Option, lang.Abstract):
    pass


@dc.dataclass(frozen=True)
class VectorSearchSimilarity(Option, lang.Final):
    similarity: Similarity


##


@dc.dataclass(frozen=True)
class VectorSearch(lang.Final):
    vec: Vector

    _: dc.KW_ONLY

    k: int = 10


@dc.dataclass(frozen=True)
class VectorHit(lang.Final):
    v: ta.Any
    score: float


@dc.dataclass(frozen=True)
class VectorHits(lang.Final):
    l: ta.Sequence[VectorHit]


##


VectorSearchInput: ta.TypeAlias = VectorSearch
VectorSearchNew: ta.TypeAlias = str
VectorSearchOutput: ta.TypeAlias = str

VectorSearchOptions: ta.TypeAlias = ServiceOption | VectorSearchOption


@dc.dataclass(frozen=True, kw_only=True)
class VectorSearchRequest(
    ServiceRequest[
        VectorSearchInput,
        VectorSearchOptions,
        VectorSearchNew,
    ],
    lang.Final,
):
    @dc.validate
    def _validate_v(self) -> bool:
        return isinstance(self.v, str)


@dc.dataclass(frozen=True, kw_only=True)
class VectorSearchResponse(ServiceResponse[VectorSearchOutput], lang.Final):
    pass


class VectorSearchService(
    Service[
        VectorSearchRequest,
        VectorSearchOptions,
        VectorSearchNew,
        VectorSearchResponse,
    ],
    lang.Abstract,
):
    @abc.abstractmethod
    def invoke(self, request: VectorSearchRequest) -> VectorSearchResponse:
        raise NotImplementedError
