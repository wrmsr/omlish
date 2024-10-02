import abc
import typing as ta

from omlish import dataclasses as dc
from omlish import lang

from .content import Content
from .models import Model
from .models import Request
from .models import RequestOption
from .models import Response
from .vectors import Vector


##


EmbeddingInput: ta.TypeAlias = Content
EmbeddingOutput: ta.TypeAlias = Vector

EmbeddingRequestOptions: ta.TypeAlias = RequestOption


@dc.dataclass(frozen=True, kw_only=True)
class EmbeddingRequest(Request[EmbeddingInput, EmbeddingRequestOptions], lang.Final):
    pass


@dc.dataclass(frozen=True, kw_only=True)
class EmbeddingResponse(Response[EmbeddingOutput], lang.Final):
    pass


class EmbeddingModel(Model[EmbeddingRequest, EmbeddingRequestOptions, EmbeddingResponse], lang.Abstract):
    @abc.abstractmethod
    def generate(self, request: EmbeddingRequest) -> EmbeddingResponse:
        raise NotImplementedError
