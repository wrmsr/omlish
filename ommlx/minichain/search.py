import abc
import typing as ta

from omlish import dataclasses as dc
from omlish import lang

from .services import Service
from .services import ServiceOption
from .services import ServiceRequest
from .services import ServiceResponse


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


SearchInput: ta.TypeAlias = str
SearchNew: ta.TypeAlias = str
SearchOutput: ta.TypeAlias = SearchHits

SearchOptions: ta.TypeAlias = ServiceOption


@dc.dataclass(frozen=True, kw_only=True)
class SearchRequest(
    ServiceRequest[
        SearchInput,
        SearchOptions,
        SearchNew,
    ],
    lang.Final,
):
    @dc.validate
    def _validate_v(self) -> bool:
        return isinstance(self.v, str)


@dc.dataclass(frozen=True, kw_only=True)
class SearchResponse(ServiceResponse[SearchOutput], lang.Final):
    pass


class SearchService(
    Service[
        SearchRequest,
        SearchOptions,
        SearchNew,
        SearchResponse,
    ],
    lang.Abstract,
):
    @abc.abstractmethod
    def invoke(self, request: SearchRequest) -> SearchResponse:
        raise NotImplementedError
