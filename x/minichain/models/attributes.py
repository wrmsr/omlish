"""
Model knowledge as a typed-value family: a model *has* whatever attributes are known about it, and unknowns are simply
absent (no wall of `| None` kwargs). Attributes are resolved by a composable `ModelAttributesProvider` chain
(static/local-first, models.dev-backed, ...), so a homemade local model with no public metadata carries only what's
known of it, while `gpt-5.5`'s context window comes from the models.dev cache - without hardcoding constants.

This is a deliberately conservative first cut; the family is open and expected to grow (modalities, more capability
flags, ...).
"""
import abc
import typing as ta

from omlish import lang
from omlish import marshal as msh
from omlish import typedvalues as tv


##


@msh.set_polymorphic_from_subclasses(naming=msh.Naming.SNAKE)
class ModelAttribute(tv.TypedValue, lang.Abstract, lang.Sealed):
    pass


ModelAttributes: ta.TypeAlias = tv.TypedValues[ModelAttribute]


##


class ContextWindow(ModelAttribute, tv.UniqueScalarTypedValue[int]):
    """Total context window, in tokens (input + output)."""


class MaxOutputTokens(ModelAttribute, tv.UniqueScalarTypedValue[int]):
    """Maximum tokens the model may generate in one response."""


class InputTokenCost(ModelAttribute, tv.UniqueScalarTypedValue[float]):
    """Cost in USD per 1M input tokens (the models.dev unit)."""


class OutputTokenCost(ModelAttribute, tv.UniqueScalarTypedValue[float]):
    """Cost in USD per 1M output tokens (the models.dev unit)."""


class SupportsTools(ModelAttribute, tv.UniqueScalarTypedValue[bool]):
    pass


class SupportsReasoning(ModelAttribute, tv.UniqueScalarTypedValue[bool]):
    pass


class SupportsStructuredOutput(ModelAttribute, tv.UniqueScalarTypedValue[bool]):
    pass


##


class ModelAttributesProvider(lang.Abstract):
    @abc.abstractmethod
    def provide_model_attributes(self, model: str) -> ta.Awaitable[ModelAttributes]:
        raise NotImplementedError
