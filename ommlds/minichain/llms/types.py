"""
TODO:
 - substantial docstrings for what each common config maps to in backends
"""
from omlish import lang
from omlish import typedvalues as tv

from ..types import Option
from ..types import Output
from .stopreasons import StopReason
from .tokens import TokenUsage


##


class LlmOption(Option, lang.Abstract, lang.Sealed):
    pass


class TopK(LlmOption, tv.UniqueScalarTypedValue[int]):
    pass


class Temperature(LlmOption, tv.UniqueScalarTypedValue[float]):
    pass


class MaxTokens(LlmOption, tv.UniqueScalarTypedValue[int]):
    pass


class MaxCompletionTokens(LlmOption, tv.UniqueScalarTypedValue[int]):
    pass


##


class LlmOutput(Output, lang.Abstract, lang.Sealed):
    pass


class StopReasonOutput(LlmOutput, tv.UniqueScalarTypedValue[StopReason]):
    pass


class InputTokenUsageOutput(LlmOutput, tv.UniqueScalarTypedValue[int]):
    pass


class TokenUsageOutput(LlmOutput, tv.UniqueScalarTypedValue[TokenUsage]):
    pass
