import typing as ta

from omcore import dataclasses as dc
from omcore import lang

from ._common import _set_class_marshal_options


##


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class CompletionUsage(lang.Final):
    completion_tokens: int
    prompt_tokens: int
    total_tokens: int

    @dc.dataclass(frozen=True, kw_only=True)
    @_set_class_marshal_options
    class CompletionTokensDetails(lang.Final):
        accepted_prediction_tokens: int | None = None
        audio_tokens: int | None = None
        reasoning_tokens: int | None = None
        rejected_prediction_tokens: int | None = None

    completion_tokens_details: CompletionTokensDetails | None = None

    @dc.dataclass(frozen=True, kw_only=True)
    @_set_class_marshal_options
    class PromptTokensDetails(lang.Final):
        audio_tokens: int | None = None
        cached_tokens: int | None = None

    prompt_tokens_details: PromptTokensDetails | None = None

    # openai-compat dialect extension (groq)
    queue_time: ta.Any | None = None
    completion_time: ta.Any | None = None
    prompt_time: ta.Any | None = None
    total_time: ta.Any | None = None
