import abc

from omlish import dataclasses as dc
from omlish import lang

from ..content.content import Content
from ..services import Request
from ..services import RequestOption
from ..services import Response
from ..services import ResponseOutput
from ..services import Service_
from .vectors import Vector


##


class EmbeddingRequestOption(RequestOption, lang.Abstract):
    pass


@dc.dataclass(frozen=True)
class EmbeddingRequest(Request[EmbeddingRequestOption]):
    content: Content


##


class EmbeddingResponseOutput(ResponseOutput, lang.Abstract):
    pass


@dc.dataclass(frozen=True)
class EmbeddingResponse(Response[EmbeddingResponseOutput]):
    vector: Vector


##


# @omlish-manifest ommlx.minichain.backends.manifests.BackendTypeManifest
class EmbeddingService(
    Service_[
        EmbeddingRequest,
        EmbeddingResponse,
    ],
    lang.Abstract,
    request=EmbeddingRequest,
    response=EmbeddingResponse,
):
    @abc.abstractmethod
    def invoke(self, request: EmbeddingRequest) -> EmbeddingResponse:
        raise NotImplementedError
