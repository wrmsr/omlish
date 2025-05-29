"""
TODO:
 - substantial docstrings for what each common config maps to in backends
"""
import enum

from omlish import dataclasses as dc
from omlish import lang
from omlish import typedvalues as tv

from ..services import RequestOption
from ..services import ResponseOutput


##


class LlmRequestOption(RequestOption, lang.Abstract):
    pass


class TopK(LlmRequestOption, tv.UniqueScalarTypedValue[int]):
    pass


class Temperature(LlmRequestOption, tv.UniqueScalarTypedValue[float]):
    pass


class MaxTokens(LlmRequestOption, tv.UniqueScalarTypedValue[int]):
    pass


##


class LlmResponseOutput(ResponseOutput, lang.Abstract):
    pass


class FinishReason(enum.Enum):
    STOP = enum.auto()
    LENGTH = enum.auto()
    TOOL_EXEC = enum.auto()
    CONTENT_FILTER = enum.auto()
    OTHER = enum.auto()


class FinishReasonOutput(LlmResponseOutput, tv.UniqueScalarTypedValue[FinishReason]):
    pass


@dc.dataclass(frozen=True)
class TokenUsage(lang.Final):
    input: int
    output: int
    total: int


class TokenUsageOutput(LlmResponseOutput, tv.UniqueScalarTypedValue[TokenUsage]):
    pass
