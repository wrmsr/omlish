import typing as ta

from omlish import dataclasses as dc
from omlish import lang

from .registries.globals import register_type
from .services import Request
from .services import Response
from .services import Service
from .types import Option
from .types import Output


##


@dc.dataclass(frozen=True, kw_only=True)
class SearchHit(lang.Final):
    title: str | None
    url: str | None
    description: str | None = None
    snippets: lang.SequenceNotStr[str] | None


@dc.dataclass(frozen=True, kw_only=True)
class SearchHits(lang.Final):
    l: ta.Sequence[SearchHit]

    total_results: int | None = None


##


class SearchOption(Option, lang.Abstract, lang.Sealed):
    pass


SearchOptions: ta.TypeAlias = SearchOption


##


class SearchOutput(Output, lang.Abstract, lang.Sealed):
    pass


SearchOutputs: ta.TypeAlias = SearchOutput


##


SearchRequest: ta.TypeAlias = Request[str, SearchOptions]

SearchResponse: ta.TypeAlias = Response[SearchHits, SearchOutputs]

# @omlish-manifest $.minichain.registries.manifests.RegistryTypeManifest
SearchService: ta.TypeAlias = Service[SearchRequest, SearchResponse]

register_type(SearchService, module=__name__)


def static_check_is_search_service[T: SearchService](t: type[T]) -> type[T]:
    return t
