import typing as ta

from omlish import dataclasses as dc
from omlish import lang

from .registry import register_type
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


##


class SearchOutput(Output, lang.Abstract, lang.Sealed):
    pass



##


SearchRequest: ta.TypeAlias = Request[str, SearchOption]

SearchResponse: ta.TypeAlias = Response[SearchHits, SearchOutput]

# @omlish-manifest ommlds.minichain.registry.RegistryTypeManifest
SearchService: ta.TypeAlias = Service[SearchRequest, SearchResponse]

register_type(SearchService, module=__name__)
