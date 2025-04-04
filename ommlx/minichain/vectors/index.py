import abc
import typing as ta

from omlish import dataclasses as dc
from omlish import lang

from ..services import Request
from ..services import RequestOption
from ..services import Response
from ..services import ResponseOutput
from ..services import Service_
from .vectors import Vector


##


@dc.dataclass(frozen=True)
class VectorIndexed(lang.Final):
    v: ta.Any
    vec: Vector


##


class VectorIndexRequestOption(RequestOption, lang.Abstract):
    pass


@dc.dataclass(frozen=True)
class VectorIndexRequest(Request[VectorIndexRequestOption]):
    i: VectorIndexed


##


class VectorIndexResponseOutput(ResponseOutput, lang.Abstract):
    pass


#


class VectorIndexResponse(Response[VectorIndexResponseOutput]):
    pass


##


# @omlish-manifest ommlx.minichain.backends.manifests.BackendTypeManifest
class VectorIndexService(
    Service_[
        VectorIndexRequest,
        VectorIndexResponse,
    ],
    lang.Abstract,
    request=VectorIndexRequest,
    response=VectorIndexResponse,
):
    @abc.abstractmethod
    def invoke(self, request: VectorIndexRequest) -> VectorIndexResponse:
        raise NotImplementedError
