import typing as ta

from omlish import dataclasses as dc
from omlish import lang

from .._common import _set_class_marshal_options
from ..completionusage import CompletionUsage
from .tokenlogprob import ChatCompletionTokenLogprob


##


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class ChatCompletionChunkChoiceDelta(lang.Final):
    content: str | None = None

    refusal: str | None = None

    role: ta.Literal[
        'developer',
        'system',
        'user',
        'assistant',
        'tool',
    ] | None = None

    @dc.dataclass(frozen=True, kw_only=True)
    class ToolCall(lang.Final):
        index: int

        id: str | None = None

        @dc.dataclass(frozen=True, kw_only=True)
        class Function(lang.Final):
            arguments: str | None = None
            name: str | None = None

        function: Function | None = None

        type: ta.Literal['function'] = dc.xfield('function', repr=False)

    tool_calls: ta.Sequence[ToolCall] | None = None


#


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class ChatCompletionChunkChoice(lang.Final):
    delta: ChatCompletionChunkChoiceDelta

    finish_reason: ta.Literal[
        'stop',
        'length',
        'tool_calls',
        'content_filter',
    ] | None = None

    index: int

    @dc.dataclass(frozen=True, kw_only=True)
    class Logprobs(lang.Final):
        content: ta.Sequence[ChatCompletionTokenLogprob] | None = None
        refusal: ta.Sequence[ChatCompletionTokenLogprob] | None = None

    logprobs: Logprobs | None = None


#


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class ChatCompletionChunk(lang.Final):
    id: str

    choices: ta.Sequence[ChatCompletionChunkChoice]

    created: int

    model: str

    object: ta.Literal['chat.completion.chunk'] = dc.xfield('chat.completion.chunk', repr=False)

    service_tier: ta.Literal[
        'auto',
        'default',
        'flex',
    ] | None = None

    system_fingerprint: str | None = None

    usage: CompletionUsage | None = None

    obfuscation: str | None = None
