# ruff: noqa: UP007 UP045
import typing as ta

from .contentpart import TextChatCompletionContentPart
from .message import ChatCompletionMessage
from .responseformat import ChatCompletionResponseFormat


##


class ChatCompletionRequestWebSearchOptionsUserLocationApproximate(ta.TypedDict, total=False):
    city: str
    country: str
    region: str
    timezone: str


class ChatCompletionRequestWebSearchOptionsUserLocation(ta.TypedDict):
    approximate: ChatCompletionRequestWebSearchOptionsUserLocationApproximate
    type: ta.Literal['approximate']


class ChatCompletionRequestWebSearchOptions(ta.TypedDict, total=False):
    search_context_size: ta.Literal[
        'low',
        'medium',
        'high',
    ]
    user_location: ChatCompletionRequestWebSearchOptionsUserLocation


#


class ChatCompletionRequestPrediction(ta.TypedDict):
    content: str | ta.Iterable[TextChatCompletionContentPart]
    type: ta.Literal['content']


#


class ChatCompletionRequestToolFunction(ta.TypedDict, total=False):
    name: ta.Required[str]
    description: str
    parameters: ta.Mapping[str, ta.Any]
    strict: bool


class ChatCompletionRequestTool(ta.TypedDict):
    function: ChatCompletionRequestToolFunction
    type: ta.Literal['function']


#


class ChatCompletionRequestStreamOptions(ta.TypedDict, total=False):
    include_usage: bool


#


class ChatCompletionRequestNamedToolChoiceFunction(ta.TypedDict):
    name: str


class ChatCompletionRequestNamedToolChoice(ta.TypedDict):
    function: ChatCompletionRequestNamedToolChoiceFunction
    type: ta.Literal['function']


#


class ChatCompletionRequestAudio(ta.TypedDict):
    format: ta.Literal[
        'wav',
        'aac',
        'mp3',
        'flac',
        'opus',
        'pcm16',
    ]

    voice: str


#


class ChatCompletionRequest(ta.TypedDict, total=False):
    messages: ta.Required[ta.Iterable[ChatCompletionMessage]]
    model: ta.Required[str]
    audio: ChatCompletionRequestAudio
    frequency_penalty: float
    logit_bias: ta.Mapping[str, int]
    logprobs: bool
    max_completion_tokens: int
    max_tokens: int
    metadata: ta.Mapping[str, str]
    modalities: ta.Sequence[ta.Literal[
        'text',
        'audio',
    ]]
    n: int
    parallel_tool_calls: bool
    prediction: ChatCompletionRequestPrediction
    presence_penalty: float
    reasoning_effort: ta.Literal[
        'low',
        'medium',
        'high',
    ]
    response_format: ChatCompletionResponseFormat
    seed: int
    service_tier: ta.Literal[
        'auto',
        'default',
        'flex',
    ]
    stop: ta.Union[str, ta.Sequence[str], None]
    store: bool
    stream_options: ChatCompletionRequestStreamOptions
    temperature: float
    tool_choice: ta.Union[
        ta.Literal[
            'none',
            'auto',
            'required',
        ],
        ChatCompletionRequestNamedToolChoice,
    ]
    tools: ta.Iterable[ChatCompletionRequestTool]
    top_logprobs: int
    top_p: float
    user: str
    web_search_options: ChatCompletionRequestWebSearchOptions
