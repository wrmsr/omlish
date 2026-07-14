"""
TODO:
 - substantial docstrings for what each common config maps to in backends
"""
from omcore import lang
from omcore import typedvalues as tv

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


class ModelNameOutput(LlmOutput, tv.UniqueScalarTypedValue[str]):
    """The concrete model that actually served a response (as reported by the backend) - e.g. 'gpt-4o-2024-08-06'."""

    # FIXME: have to normalize somehow.. whatever it's incremental
    # TODO: ModelName newtype / box?
    # TODO: move to mc/models? ModelOutputs?
