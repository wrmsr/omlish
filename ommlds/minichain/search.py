import typing as ta

from omlish import dataclasses as dc
from omlish import lang

from .registry import register_type
from .services import Request
from .services import RequestOption
from .services import Response
from .services import ResponseOutput
from .services import Service


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


class SearchRequestOption(RequestOption, lang.Abstract, lang.Sealed):
    pass


SearchRequest: ta.TypeAlias = Request[str, SearchRequestOption]


##


class SearchResponseOutput(ResponseOutput, lang.Abstract, lang.Sealed):
    pass


SearchResponse: ta.TypeAlias = Response[SearchHits, SearchResponseOutput]


##


# @omlish-manifest ommlds.minichain.registry.RegistryTypeManifest
SearchService: ta.TypeAlias = Service[SearchRequest, SearchResponse]

register_type(SearchService, module=__name__)
