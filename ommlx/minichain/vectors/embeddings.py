import abc
import typing as ta

from omlish import dataclasses as dc
from omlish import lang

from ..content.content import Content
from ..models import Model
from ..models import ModelOption
from ..models import ModelRequest
from ..models import ModelResponse
from .vectors import Vector


##


EmbeddingInput: ta.TypeAlias = Content
EmbeddingNew: ta.TypeAlias = ta.Any
EmbeddingOutput: ta.TypeAlias = Vector

EmbeddingOptions: ta.TypeAlias = ModelOption


@dc.dataclass(frozen=True, kw_only=True)
class EmbeddingRequest(
    ModelRequest[
        EmbeddingInput,
        EmbeddingOptions,
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
        EmbeddingOptions,
        EmbeddingNew,
        EmbeddingResponse,
    ],
    lang.Abstract,
):
    @abc.abstractmethod
    def invoke(self, request: EmbeddingRequest) -> EmbeddingResponse:
        raise NotImplementedError
