import abc
import typing as ta

from omlish import dataclasses as dc
from omlish import lang

from ..content import Content
from ..models import Model
from ..models import Request
from ..models import RequestOption
from ..models import Response
from .vectors import Vector


##


EmbeddingInput: ta.TypeAlias = Content
EmbeddingNew: ta.TypeAlias = ta.Any
EmbeddingOutput: ta.TypeAlias = Vector

EmbeddingRequestOptions: ta.TypeAlias = RequestOption


@dc.dataclass(frozen=True, kw_only=True)
class EmbeddingRequest(
    Request[
        EmbeddingInput,
        EmbeddingRequestOptions,
        EmbeddingNew,
    ],
    lang.Final,
):
    pass


@dc.dataclass(frozen=True, kw_only=True)
class EmbeddingResponse(Response[EmbeddingOutput], lang.Final):
    pass


class EmbeddingModel(
    Model[
        EmbeddingRequest,
        EmbeddingRequestOptions,
        EmbeddingNew,
        EmbeddingResponse,
    ],
    lang.Abstract,
):
    @abc.abstractmethod
    def invoke(self, request: EmbeddingRequest) -> EmbeddingResponse:
        raise NotImplementedError
