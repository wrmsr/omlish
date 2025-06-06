"""
https://platform.openai.com/docs/api-reference/introduction
https://github.com/openai/openai-openapi/blob/master/openapi.yaml
"""
import typing as ta


##


class CompletionTokensDetails(ta.TypedDict, total=False):
    accepted_prediction_tokens: int
    audio_tokens: int
    reasoning_tokens: int
    rejected_prediction_tokens: int


class PromptTokensDetails(ta.TypedDict, total=False):
    audio_tokens: int
    cached_tokens: int


class CompletionUsage(ta.TypedDict):
    completion_tokens: int
    prompt_tokens: int
    total_tokens: int
    completion_tokens_details: ta.NotRequired[CompletionTokensDetails]
    prompt_tokens_details: ta.NotRequired[PromptTokensDetails]


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


##


class ChatCompletionAnnotationUrlCitation(ta.TypedDict):
    end_index: int
    start_index: int
    title: str
    url: str


class ChatCompletionAnnotation(ta.TypedDict):
    type: ta.Literal['url_citation']
    url_citation: ChatCompletionAnnotationUrlCitation


class ChatCompletionAudio(ta.TypedDict):
    id: str
    data: str
    expires_at: int
    transcript: str


class ChatCompletionFunction(ta.TypedDict):
    arguments: str
    name: str


class ChatCompletionMessageToolCall(ta.TypedDict):
    id: str
    function: ChatCompletionFunction
    type: ta.Literal['function']


class ChatCompletionMessage(ta.TypedDict, total=False):
    content: str
    refusal: str
    role: ta.Required[ta.Literal['assistant']]
    annotations: ta.Sequence[ChatCompletionAnnotation]
    audio: ChatCompletionAudio
    tool_calls: ta.Sequence[ChatCompletionMessageToolCall]


class ChatCompletionChoiceLogprobs(ta.TypedDict, total=False):
    content: ta.Sequence[ChatCompletionTokenLogprob]
    refusal: ta.Sequence[ChatCompletionTokenLogprob]


class ChatCompletionChoice(ta.TypedDict):
    finish_reason: ta.Literal['stop', 'length', 'tool_calls', 'content_filter', 'function_call']
    index: int
    logprobs: ta.NotRequired[ChatCompletionChoiceLogprobs]
    message: ChatCompletionMessage


class ChatCompletion(ta.TypedDict):
    id: str
    choices: ta.Sequence[ChatCompletionChoice]
    created: int
    model: str
    object: ta.Literal['chat.completion']
    service_tier: ta.NotRequired[ta.Literal['auto', 'default', 'flex']]
    system_fingerprint: ta.NotRequired[str]
    usage: ta.NotRequired[CompletionUsage]


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
