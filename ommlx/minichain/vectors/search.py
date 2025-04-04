import typing as ta

from omlish import dataclasses as dc
from omlish import lang

from ..services import Request
from ..services import RequestOption
from ..services import Response
from ..services import ResponseOutput
from ..services import Service_
from .similarity import Similarity
from .vectors import Vector


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


class VectorSearchRequestOption(RequestOption, lang.Abstract):
    pass


@dc.dataclass(frozen=True)
class VectorSearchSimilarity(VectorSearchRequestOption, lang.Final):
    similarity: Similarity


#


@dc.dataclass(frozen=True, kw_only=True)
class VectorSearchRequest(Request[VectorSearchRequestOption]):
    search: VectorSearch


##


class VectorSearchResponseOutput(ResponseOutput, lang.Abstract):
    pass


#


@dc.dataclass(frozen=True, kw_only=True)
class VectorSearchResponse(Response[VectorSearchResponseOutput]):
    hits: VectorHits


##


# @omlish-manifest ommlx.minichain.backends.manifests.BackendTypeManifest
class VectorSearchService(  # noqa
    Service_[
        VectorSearchRequest,
        VectorSearchResponse,
    ],
    lang.Abstract,
    request=VectorSearchRequest,
    response=VectorSearchResponse,
):
    pass
