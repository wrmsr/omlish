import typing as ta

from omlish import dataclasses as dc
from omlish import lang

from ..registries.globals import register_type
from ..services import Request
from ..services import Response
from ..services import Service
from ..types import Option
from ..types import Output
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


class VectorSearchOption(Option, lang.Abstract, lang.Sealed):
    pass


@dc.dataclass(frozen=True)
class VectorSearchSimilarity(VectorSearchOption, lang.Final):
    similarity: Similarity


VectorSearchOptions: ta.TypeAlias = VectorSearchOption


##


class VectorSearchOutput(Output, lang.Abstract, lang.Sealed):
    pass


VectorSearchOutputs: ta.TypeAlias = VectorSearchOutput


##


VectorSearchRequest: ta.TypeAlias = Request[VectorSearch, VectorSearchOptions]

VectorSearchResponse: ta.TypeAlias = Response[VectorHits, VectorSearchOutputs]

# @omlish-manifest $.minichain.registries.manifests.RegistryTypeManifest
VectorSearchService: ta.TypeAlias = Service[VectorSearchRequest, VectorSearchResponse]

register_type(VectorSearchService, module=__name__)


def static_check_is_vector_search_service[T: VectorSearchService](t: type[T]) -> type[T]:
    return t
