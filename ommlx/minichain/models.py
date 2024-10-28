import abc
import enum
import typing as ta

from omlish import dataclasses as dc
from omlish import lang

from .options import Option
from .services import Service
from .services import ServiceOption
from .services import ServiceRequest
from .services import ServiceResponse


ModelInputT = ta.TypeVar('ModelInputT')
ModelOptionT = ta.TypeVar('ModelOptionT', bound='Option')
ModelNewT = ta.TypeVar('ModelNewT')
ModelOutputT = ta.TypeVar('ModelOutputT')

ModelRequestT = ta.TypeVar('ModelRequestT', bound='ModelRequest')
ModelResponseT = ta.TypeVar('ModelResponseT', bound='ModelResponse')


##


class FinishReason(enum.Enum):
    STOP = enum.auto()
    LENGTH = enum.auto()
    TOOL_EXEC = enum.auto()
    CONTENT_FILTER = enum.auto()
    OTHER = enum.auto()


@dc.dataclass(frozen=True)
class TokenUsage(lang.Final):
    input: int
    output: int
    total: int


##


class ModelOption(Option, lang.Abstract):
    pass


##


ModelOptions: ta.TypeAlias = ServiceOption | ModelOption


@dc.dataclass(frozen=True, kw_only=True)
class ModelRequest(
    ServiceRequest[
        ModelInputT,
        ModelOptionT,
        ModelNewT,
    ],
    lang.Abstract,
):
    pass


@dc.dataclass(frozen=True, kw_only=True)
class ModelResponse(ServiceResponse[ModelOutputT], lang.Abstract):
    usage: TokenUsage | None = dc.xfield(None, repr_fn=dc.opt_repr)
    reason: FinishReason | None = dc.xfield(None, repr_fn=dc.opt_repr)


class Model(
    Service[
        ModelRequestT,
        ModelOptionT,
        ModelNewT,
        ModelResponseT,
    ],
    lang.Abstract,
):
    @abc.abstractmethod
    def invoke(self, request: ModelRequestT) -> ModelResponseT:
        raise NotImplementedError
