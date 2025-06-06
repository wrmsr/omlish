import typing as ta


##


class CompletionUsageCompletionTokensDetails(ta.TypedDict, total=False):
    accepted_prediction_tokens: int
    audio_tokens: int
    reasoning_tokens: int
    rejected_prediction_tokens: int


class CompletionUsagePromptTokensDetails(ta.TypedDict, total=False):
    audio_tokens: int
    cached_tokens: int


class CompletionUsage(ta.TypedDict):
    completion_tokens: int
    prompt_tokens: int
    total_tokens: int
    completion_tokens_details: ta.NotRequired[CompletionUsageCompletionTokensDetails]
    prompt_tokens_details: ta.NotRequired[CompletionUsagePromptTokensDetails]
