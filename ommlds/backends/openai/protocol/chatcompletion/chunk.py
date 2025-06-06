import typing as ta

from .tokenlogprob import ChatCompletionTokenLogprob


##


class ChatCompletionChunkChoiceDeltaToolCallFunction(ta.TypedDict, total=False):
    arguments: str
    name: str


class ChatCompletionChunkChoiceDeltaToolCall(ta.TypedDict):
    index: int
    id: ta.NotRequired[str]
    function: ta.NotRequired[ChatCompletionChunkChoiceDeltaToolCallFunction]
    type: ta.Literal['function']


#


class ChatCompletionChunkChoiceDelta(ta.TypedDict, total=False):
    content: str
    refusal: str
    role: ta.Literal[
        'developer',
        'system',
        'user',
        'assistant',
        'tool',
    ]
    tool_calls: ta.Sequence[ChatCompletionChunkChoiceDeltaToolCall]


#


class ChatCompletionChunkChoiceLogprobs(ta.TypedDict, total=False):
    content: ta.Sequence[ChatCompletionTokenLogprob]
    refusal: ta.Sequence[ChatCompletionTokenLogprob]


class ChatCompletionChunkChoice(ta.TypedDict):
    delta: ChatCompletionChunkChoiceDelta
    finish_reason: ta.NotRequired[ta.Literal[
        'stop',
        'length',
        'tool_calls',
        'content_filter',
    ]]
    index: int
    logprobs: ta.NotRequired[ChatCompletionChunkChoiceLogprobs]


#


class ChatCompletionChunk(ta.TypedDict):
    id: str
    choices: ta.Sequence[ChatCompletionChunkChoice]
    created: int
    model: str
    object: ta.Literal['chat.completion.chunk']
    service_tier: ta.NotRequired[ta.Literal[
        'auto',
        'default',
        'flex',
    ]]
    system_fingerprint: ta.NotRequired[str]
