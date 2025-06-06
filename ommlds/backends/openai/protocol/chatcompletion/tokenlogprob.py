import typing as ta


##


class ChatCompletionTokenLogprobTopLogprob(ta.TypedDict):
    token: str
    bytes: ta.NotRequired[ta.Sequence[int]]
    logprob: float


class ChatCompletionTokenLogprob(ta.TypedDict):
    token: str
    bytes: ta.NotRequired[ta.Sequence[int]]
    logprob: float
    top_logprobs: ta.Sequence[ChatCompletionTokenLogprobTopLogprob]
