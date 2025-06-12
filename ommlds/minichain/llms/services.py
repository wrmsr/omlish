"""
TODO:
 - substantial docstrings for what each common config maps to in backends
"""
import enum

from omlish import dataclasses as dc
from omlish import lang
from omlish import typedvalues as tv

from ..types import Option
from ..types import Output


##


class LlmOption(Option, lang.Abstract, lang.Sealed):
    pass


class TopK(LlmOption, tv.UniqueScalarTypedValue[int]):
    pass


class Temperature(LlmOption, tv.UniqueScalarTypedValue[float]):
    pass


class MaxTokens(LlmOption, tv.UniqueScalarTypedValue[int]):
    pass


##


class LlmOutput(Output, lang.Abstract, lang.Sealed):
    pass


class FinishReason(enum.Enum):
    STOP = enum.auto()
    LENGTH = enum.auto()
    TOOL_EXEC = enum.auto()
    CONTENT_FILTER = enum.auto()
    OTHER = enum.auto()


class FinishReasonOutput(LlmOutput, tv.UniqueScalarTypedValue[FinishReason]):
    pass


@dc.dataclass(frozen=True)
class TokenUsage(lang.Final):
    input: int
    output: int
    total: int


class TokenUsageOutput(LlmOutput, tv.UniqueScalarTypedValue[TokenUsage]):
    pass
