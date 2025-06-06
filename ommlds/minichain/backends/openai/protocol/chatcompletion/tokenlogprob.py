import typing as ta


##


class ChatCompletionTopLogprob(ta.TypedDict):
    token: str
    bytes: ta.NotRequired[ta.Sequence[int]]
    logprob: float


class ChatCompletionTokenLogprob(ta.TypedDict):
    token: str
    bytes: ta.NotRequired[ta.Sequence[int]]
    logprob: float
    top_logprobs: ta.Sequence[ChatCompletionTopLogprob]
