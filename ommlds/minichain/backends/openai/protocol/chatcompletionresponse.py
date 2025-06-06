import typing as ta

from .chatcompletiontokenlogprob import ChatCompletionTokenLogprob
from .completionusage import CompletionUsage


##


class ChatCompletionResponseAnnotationUrlCitation(ta.TypedDict):
    end_index: int
    start_index: int
    title: str
    url: str


class ChatCompletionResponseAnnotation(ta.TypedDict):
    type: ta.Literal['url_citation']
    url_citation: ChatCompletionResponseAnnotationUrlCitation


#


class ChatCompletionResponseAudio(ta.TypedDict):
    id: str
    data: str
    expires_at: int
    transcript: str


#


class ChatCompletionResponseFunction(ta.TypedDict):
    arguments: str
    name: str


class ChatCompletionResponseMessageToolCall(ta.TypedDict):
    id: str
    function: ChatCompletionResponseFunction
    type: ta.Literal['function']


#


class ChatCompletionResponseMessage(ta.TypedDict, total=False):
    content: str
    refusal: str
    role: ta.Required[ta.Literal['assistant']]
    annotations: ta.Sequence[ChatCompletionResponseAnnotation]
    audio: ChatCompletionResponseAudio
    tool_calls: ta.Sequence[ChatCompletionResponseMessageToolCall]


#


class ChatCompletionResponseChoiceLogprobs(ta.TypedDict, total=False):
    content: ta.Sequence[ChatCompletionTokenLogprob]
    refusal: ta.Sequence[ChatCompletionTokenLogprob]


class ChatCompletionResponseChoice(ta.TypedDict):
    finish_reason: ta.Literal[
        'stop',
        'length',
        'tool_calls',
        'content_filter',
        'function_call',
    ]
    index: int
    logprobs: ta.NotRequired[ChatCompletionResponseChoiceLogprobs]
    message: ChatCompletionResponseMessage


#


class ChatCompletionResponse(ta.TypedDict):
    id: str
    choices: ta.Sequence[ChatCompletionResponseChoice]
    created: int
    model: str
    object: ta.Literal['chat.completion']
    service_tier: ta.NotRequired[ta.Literal[
        'auto',
        'default',
        'flex',
    ]]
    system_fingerprint: ta.NotRequired[str]
    usage: ta.NotRequired[CompletionUsage]
