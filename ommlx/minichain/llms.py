import enum

from omlish import dataclasses as dc
from omlish import lang
from omlish import typedvalues as tv

from .services import RequestOption
from .services import ResponseOutput


##


class LlmRequestOption(RequestOption, lang.Abstract):
    pass


class TopK(LlmRequestOption, tv.ScalarTypedValue[int], tv.UniqueTypedValue, lang.Final):
    pass


class Temperature(LlmRequestOption, tv.ScalarTypedValue[float], tv.UniqueTypedValue, lang.Final):
    pass


class MaxTokens(LlmRequestOption, tv.ScalarTypedValue[int], tv.UniqueTypedValue, lang.Final):
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


class FinishReasonOutput(LlmResponseOutput, tv.ScalarTypedValue[FinishReason], tv.UniqueTypedValue, lang.Final):
    pass


@dc.dataclass(frozen=True)
class TokenUsage(lang.Final):
    input: int
    output: int
    total: int


class TokenUsageOutput(LlmResponseOutput, tv.ScalarTypedValue[TokenUsage], tv.UniqueTypedValue, lang.Final):
    pass
