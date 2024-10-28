import abc
import typing as ta

from omlish import dataclasses as dc
from omlish import lang

from ..services import Service
from ..services import ServiceOption
from ..services import ServiceRequest
from ..services import ServiceResponse
from .vectors import Vector


##


@dc.dataclass(frozen=True)
class VectorIndexed(lang.Final):
    v: ta.Any
    vec: Vector


##


VectorIndexInput: ta.TypeAlias = VectorIndexed
VectorIndexNew: ta.TypeAlias = VectorIndexInput
VectorIndexOutput: ta.TypeAlias = None

VectorIndexOptions: ta.TypeAlias = ServiceOption


@dc.dataclass(frozen=True, kw_only=True)
class VectorIndexRequest(
    ServiceRequest[
        VectorIndexInput,
        VectorIndexOptions,
        VectorIndexNew,
    ],
    lang.Final,
):
    pass


@dc.dataclass(frozen=True, kw_only=True)
class VectorIndexResponse(ServiceResponse[VectorIndexOutput], lang.Final):
    pass


class VectorIndexService(
    Service[
        VectorIndexRequest,
        VectorIndexOptions,
        VectorIndexNew,
        VectorIndexResponse,
    ],
    lang.Abstract,
):
    @abc.abstractmethod
    def invoke(self, request: VectorIndexRequest) -> VectorIndexResponse:
        raise NotImplementedError
