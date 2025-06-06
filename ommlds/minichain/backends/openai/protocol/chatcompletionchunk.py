import typing as ta

from .chatcompletiontokenlogprob import ChatCompletionTokenLogprob


##


class ChatCompletionChoiceDeltaToolCallFunction(ta.TypedDict, total=False):
    arguments: str
    name: str


class ChatCompletionChoiceDeltaToolCall(ta.TypedDict):
    index: int
    id: ta.NotRequired[str]
    function: ta.NotRequired[ChatCompletionChoiceDeltaToolCallFunction]
    type: ta.Literal['function']


class ChatCompletionChoiceDelta(ta.TypedDict, total=False):
    content: str
    refusal: str
    role: ta.Literal['developer', 'system', 'user', 'assistant', 'tool']
    tool_calls: ta.Sequence[ChatCompletionChoiceDeltaToolCall]


class ChatCompletionChunkChoiceLogprobs(ta.TypedDict, total=False):
    content: ta.Sequence[ChatCompletionTokenLogprob]
    refusal: ta.Sequence[ChatCompletionTokenLogprob]


class ChatCompletionChunkChoice(ta.TypedDict):
    delta: ChatCompletionChoiceDelta
    finish_reason: ta.NotRequired[ta.Literal['stop', 'length', 'tool_calls', 'content_filter', 'function_call']]
    index: int
    logprobs: ta.NotRequired[ChatCompletionChunkChoiceLogprobs]


class ChatCompletionChunk(ta.TypedDict):
    id: str
    choices: list[ChatCompletionChunkChoice]
    created: int
    model: str
    object: ta.Literal['chat.completion.chunk']
    service_tier: ta.NotRequired[ta.Literal['auto', 'default', 'flex']]
    system_fingerprint:ta.NotRequired[str]
