import typing as ta

from omlish import dataclasses as dc
from omlish import lang

from .._common import _set_class_marshal_options
from ..completionusage import CompletionUsage
from .tokenlogprob import ChatCompletionTokenLogprob


##


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class ChatCompletionResponseMessage(lang.Final):
    content: str | None = None
    refusal: str | None = None
    role: ta.Literal['assistant'] = dc.xfield('assistant', repr=False)

    @dc.dataclass(frozen=True, kw_only=True)
    @_set_class_marshal_options
    class Annotation(lang.Final):
        type: ta.Literal['url_citation'] = dc.xfield('url_citation', repr=False)

        @dc.dataclass(frozen=True, kw_only=True)
        @_set_class_marshal_options
        class UrlCitation(lang.Final):
            end_index: int
            start_index: int
            title: str
            url: str

        url_citation: UrlCitation

    annotations: ta.Sequence[Annotation] | None = None

    @dc.dataclass(frozen=True, kw_only=True)
    @_set_class_marshal_options
    class Audio(lang.Final):
        id: str
        data: str
        expires_at: int
        transcript: str

    audio: Audio | None = None

    @dc.dataclass(frozen=True, kw_only=True)
    @_set_class_marshal_options
    class ToolCall(lang.Final):
        id: str

        @dc.dataclass(frozen=True, kw_only=True)
        @_set_class_marshal_options
        class Function(lang.Final):
            arguments: str
            name: str

        function: Function

        type: ta.Literal['function'] = dc.xfield('function', repr=False)

    tool_calls: ta.Sequence[ToolCall] | None = None


#


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class ChatCompletionResponseChoice(lang.Final):
    finish_reason: ta.Literal[
        'stop',
        'length',
        'tool_calls',
        'content_filter',
    ]

    index: int

    @dc.dataclass(frozen=True, kw_only=True)
    @_set_class_marshal_options
    class Logprobs(lang.Final):
        content: ta.Sequence[ChatCompletionTokenLogprob] | None = None
        refusal: ta.Sequence[ChatCompletionTokenLogprob] | None = None

    logprobs: Logprobs | None = None

    message: ChatCompletionResponseMessage


#


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class ChatCompletionResponse(lang.Final):
    id: str

    choices: ta.Sequence[ChatCompletionResponseChoice]

    created: int

    model: str

    object: ta.Literal['chat.completion'] = dc.xfield('chat.completion', repr=False)

    service_tier: ta.Literal[
        'auto',
        'default',
        'flex',
    ] | None = None

    system_fingerprint: str | None = None

    usage: CompletionUsage | None = None
