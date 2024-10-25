import abc
import typing as ta

from omlish import dataclasses as dc
from omlish import lang

from ..content import Content
from ..models import Model
from ..models import ModelRequest
from ..models import ModelRequestOption
from ..models import ModelResponse
from .vectors import Vector


##


EmbeddingInput: ta.TypeAlias = Content
EmbeddingNew: ta.TypeAlias = ta.Any
EmbeddingOutput: ta.TypeAlias = Vector

EmbeddingRequestOptions: ta.TypeAlias = ModelRequestOption


@dc.dataclass(frozen=True, kw_only=True)
class EmbeddingRequest(
    ModelRequest[
        EmbeddingInput,
        EmbeddingRequestOptions,
        EmbeddingNew,
    ],
    lang.Final,
):
    pass


@dc.dataclass(frozen=True, kw_only=True)
class EmbeddingResponse(ModelResponse[EmbeddingOutput], lang.Final):
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
