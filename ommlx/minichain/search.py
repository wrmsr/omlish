import typing as ta

from omlish import dataclasses as dc
from omlish import lang

from .services import Request
from .services import RequestOption
from .services import Response
from .services import ResponseOutput
from .services import Service_


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


class SearchRequestOption(RequestOption, lang.Abstract):
    pass


#


@dc.dataclass(frozen=True)
class SearchRequest(Request):
    query: str


##


class SearchResponseOutput(ResponseOutput, lang.Abstract):
    pass


#


@dc.dataclass(frozen=True)
class SearchResponse(Response):
    hits: SearchHits


##


# @omlish-manifest ommlx.minichain.backends.manifests.BackendTypeManifest
class SearchService(  # noqa
    Service_[
        SearchRequest,
        SearchResponse,
    ],
    lang.Abstract,
    request=SearchRequest,
    response=SearchResponse,
):
    pass
