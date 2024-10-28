import abc
import typing as ta

from omlish import dataclasses as dc
from omlish import lang

from .generative import Generative
from .models import Model
from .models import ModelRequest
from .models import ModelResponse
from .services import RequestOption


##


SearchInput: ta.TypeAlias = str
SearchNew: ta.TypeAlias = str
SearchOutput: ta.TypeAlias = str

SearchRequestOptions: ta.TypeAlias = RequestOption


@dc.dataclass(frozen=True, kw_only=True)
class SearchRequest(
    ModelRequest[
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
class SearchHit(lang.Final):
    title: str
    link: str
    snippet: str | None


@dc.dataclass(frozen=True, kw_only=True)
class SearchHits(lang.Final):
    l: ta.Sequence[SearchHit]


@dc.dataclass(frozen=True, kw_only=True)
class SearchResponse(ModelResponse[SearchOutput], lang.Final):
    hits: SearchHits


class SearchModel(
    Model[
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
