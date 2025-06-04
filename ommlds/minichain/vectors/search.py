import typing as ta

from omlish import dataclasses as dc
from omlish import lang

from ..registry import register_type
from ..services import Request
from ..services import RequestOption
from ..services import Response
from ..services import ResponseOutput
from ..services import Service
from .similarity import Similarity
from .types import Vector


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


class VectorSearchRequestOption(RequestOption, lang.Abstract, lang.Sealed):
    pass


@dc.dataclass(frozen=True)
class VectorSearchSimilarity(VectorSearchRequestOption, lang.Final):
    similarity: Similarity


VectorSearchRequest: ta.TypeAlias = Request[VectorSearch, VectorSearchRequestOption]


##


class VectorSearchResponseOutput(ResponseOutput, lang.Abstract, lang.Sealed):
    pass


VectorSearchResponse: ta.TypeAlias = Response[VectorHits, VectorSearchResponseOutput]


##


# @omlish-manifest ommlds.minichain.registry.RegistryTypeManifest
VectorSearchService: ta.TypeAlias = Service[VectorSearchRequest, VectorSearchResponse]

register_type(VectorSearchService, module=__name__)
