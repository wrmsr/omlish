# ruff: noqa: UP007
import typing as ta

from omlish import dataclasses as dc
from omlish import lang

from .contentpart import TextChatCompletionContentPart
from .message import ChatCompletionMessage
from .responseformat import ChatCompletionResponseFormat


##


@dc.dataclass(frozen=True, kw_only=True)
class ChatCompletionRequestWebSearchOptions(lang.Final):
    search_context_size: ta.Literal[
        'low',
        'medium',
        'high',
    ] | None = None

    @dc.dataclass(frozen=True, kw_only=True)
    class UserLocation(lang.Final):
        @dc.dataclass(frozen=True, kw_only=True)
        class Approximate(lang.Final):
            city: str | None = None
            country: str | None = None
            region: str | None = None
            timezone: str | None = None

        approximate: Approximate
        type: ta.Literal['approximate'] | None = None

    user_location: UserLocation | None = None


#


@dc.dataclass(frozen=True, kw_only=True)
class ChatCompletionRequestPrediction(lang.Final):
    content: str | ta.Iterable[TextChatCompletionContentPart]
    type: ta.Literal['content'] | None = None


#


@dc.dataclass(frozen=True, kw_only=True)
class ChatCompletionRequestTool(lang.Final):
    @dc.dataclass(frozen=True, kw_only=True)
    class Function(lang.Final):
        name: str
        description: str | None = None
        parameters: ta.Mapping[str, ta.Any] | None = None
        strict: bool | None = None

    function: Function
    type: ta.Literal['function'] | None = None


#


@dc.dataclass(frozen=True, kw_only=True)
class ChatCompletionRequestNamedToolChoice(lang.Final):
    @dc.dataclass(frozen=True, kw_only=True)
    class Function(lang.Final):
        name: str

    function: Function
    type: ta.Literal['function'] | None = None


#


@dc.dataclass(frozen=True, kw_only=True)
class ChatCompletionRequestAudio(lang.Final):
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


@dc.dataclass(frozen=True, kw_only=True)
class ChatCompletionRequest(lang.Final):
    messages: ta.Iterable[ChatCompletionMessage]

    model: str

    audio: ChatCompletionRequestAudio | None = None

    frequency_penalty: float | None = None
    logit_bias: ta.Mapping[str, int] | None = None
    logprobs: bool | None = None

    max_completion_tokens: int | None = None
    max_tokens: int | None = None

    metadata: ta.Mapping[str, str] | None = None

    modalities: ta.Sequence[ta.Literal[
        'text',
        'audio',
    ]] | None = None

    n: int | None = None

    parallel_tool_calls: bool | None = None

    prediction: ChatCompletionRequestPrediction | None = None

    presence_penalty: float | None = None

    reasoning_effort: ta.Literal[
        'low',
        'medium',
        'high',
    ] | None = None

    response_format: ChatCompletionResponseFormat | None = None

    seed: int | None = None

    service_tier: ta.Literal[
        'auto',
        'default',
        'flex',
    ] | None = None

    stop: ta.Union[str, ta.Sequence[str], None] = None

    store: bool | None = None

    @dc.dataclass(frozen=True, kw_only=True)
    class StreamOptions(lang.Final):
        include_usage: bool | None = None

    stream_options: StreamOptions | None = None

    temperature: float | None = None

    tool_choice: ta.Union[
        ta.Literal[
            'none',
            'auto',
            'required',
        ],
        ChatCompletionRequestNamedToolChoice,
    ] | None = None

    tools: ta.Iterable[ChatCompletionRequestTool] | None = None

    top_logprobs: int | None = None
    top_p: float | None = None

    user: str | None = None

    web_search_options: ChatCompletionRequestWebSearchOptions | None = None
