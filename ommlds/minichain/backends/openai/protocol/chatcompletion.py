import typing as ta

from .chatcompletiontokenlogprob import ChatCompletionTokenLogprob
from .completionusage import CompletionUsage


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
