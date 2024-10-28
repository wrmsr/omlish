import abc
import typing as ta

from omlish import dataclasses as dc
from omlish import lang

from .generative import Generative
from .services import Request
from .services import RequestOption
from .services import Response
from .services import Service


##


@dc.dataclass(frozen=True, kw_only=True)
class SearchHit(lang.Final):
    title: str | None
    link: str | None
    snippet: str | None


@dc.dataclass(frozen=True, kw_only=True)
class SearchHits(lang.Final):
    l: ta.Sequence[SearchHit]

    total_results: int | None = None


##


SearchInput: ta.TypeAlias = str
SearchNew: ta.TypeAlias = str
SearchOutput: ta.TypeAlias = SearchHits

SearchRequestOptions: ta.TypeAlias = RequestOption


@dc.dataclass(frozen=True, kw_only=True)
class SearchRequest(
    Request[
        SearchInput,
        SearchRequestOptions,
        SearchNew,
    ],
    lang.Final,
):
    @dc.validate
    def _validate_v(self) -> bool:
        return isinstance(self.v, str)


@dc.dataclass(frozen=True, kw_only=True)
class SearchResponse(Response[SearchOutput], lang.Final):
    pass


class SearchService(
    Service[
        SearchRequest,
        SearchRequestOptions,
        SearchNew,
        SearchResponse,
    ],
    Generative,
    lang.Abstract,
):
    @abc.abstractmethod
    def invoke(self, request: SearchRequest) -> SearchResponse:
        raise NotImplementedError
