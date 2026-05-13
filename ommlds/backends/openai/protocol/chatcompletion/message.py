import typing as ta

from omlish import dataclasses as dc
from omlish import lang

from .._common import _set_class_marshal_options
from .contentpart import ChatCompletionContentPart
from .contentpart import RefusalChatCompletionContentPart
from .contentpart import TextChatCompletionContentPart


##


class ChatCompletionMessage(lang.Abstract, lang.Sealed):
    pass


#


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class DeveloperChatCompletionMessage(ChatCompletionMessage, lang.Final):
    content: str | ta.Iterable[TextChatCompletionContentPart]
    name: str | None = None


#


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class SystemChatCompletionMessage(ChatCompletionMessage, lang.Final):
    content: str | ta.Iterable[TextChatCompletionContentPart]
    name: str | None = None


#


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class UserChatCompletionMessage(ChatCompletionMessage, lang.Final):
    content: str | ta.Iterable[ChatCompletionContentPart]
    name: str | None = None


#


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class AssistantChatCompletionMessage(ChatCompletionMessage, lang.Final):
    @dc.dataclass(frozen=True, kw_only=True)
    @_set_class_marshal_options
    class Audio(lang.Final):
        id: str

    audio: Audio | None = None

    content: str | ta.Iterable[TextChatCompletionContentPart | RefusalChatCompletionContentPart] | None = None

    name: str | None = None

    refusal: str | None = None

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

    tool_calls: ta.Iterable[ToolCall] | None = None


#


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class ToolChatCompletionMessage(ChatCompletionMessage, lang.Final):
    content: str | ta.Iterable[TextChatCompletionContentPart]
    tool_call_id: str


#


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class FunctionChatCompletionMessage(ChatCompletionMessage, lang.Final):
    content: str | None
    name: str
