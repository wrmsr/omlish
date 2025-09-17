import typing as ta

from omlish import dataclasses as dc
from omlish import lang

from .contentpart import ChatCompletionContentPart
from .contentpart import RefusalChatCompletionContentPart
from .contentpart import TextChatCompletionContentPart


##


class ChatCompletionMessage(lang.Abstract, lang.Sealed):
    _ROLE_TAG: ta.ClassVar[str]


#


@dc.dataclass(frozen=True, kw_only=True)
class DeveloperChatCompletionMessage(ChatCompletionMessage, lang.Final):
    _ROLE_TAG: ta.ClassVar[str] = 'developer'

    content: str | ta.Iterable[TextChatCompletionContentPart]
    name: str | None = None


#


@dc.dataclass(frozen=True, kw_only=True)
class SystemChatCompletionMessage(ChatCompletionMessage, lang.Final):
    _ROLE_TAG: ta.ClassVar[str] = 'system'

    content: str | ta.Iterable[TextChatCompletionContentPart]
    name: str | None = None


#


@dc.dataclass(frozen=True, kw_only=True)
class UserChatCompletionMessage(ChatCompletionMessage, lang.Final):
    _ROLE_TAG: ta.ClassVar[str] = 'user'

    content: str | ta.Iterable[ChatCompletionContentPart]
    name: str | None = None


#


@dc.dataclass(frozen=True, kw_only=True)
class AssistantChatCompletionMessage(ChatCompletionMessage, lang.Final):
    _ROLE_TAG: ta.ClassVar[str] = 'assistant'

    @dc.dataclass(frozen=True, kw_only=True)
    class Audio(lang.Final):
        id: str

    audio: Audio | None = None

    content: str | ta.Iterable[TextChatCompletionContentPart | RefusalChatCompletionContentPart] | None = None

    name: str | None = None

    refusal: str | None = None

    @dc.dataclass(frozen=True, kw_only=True)
    class ToolCall(lang.Final):
        id: str

        @dc.dataclass(frozen=True, kw_only=True)
        class Function(lang.Final):
            arguments: str
            name: str

        function: Function

        type: ta.Literal['function'] = dc.xfield('function', repr=False)

    tool_calls: ta.Iterable[ToolCall] | None = None


#


@dc.dataclass(frozen=True, kw_only=True)
class ToolChatCompletionMessage(ChatCompletionMessage, lang.Final):
    _ROLE_TAG: ta.ClassVar[str] = 'tool'

    content: str | ta.Iterable[TextChatCompletionContentPart]
    tool_call_id: str


#


@dc.dataclass(frozen=True, kw_only=True)
class FunctionChatCompletionMessage(ChatCompletionMessage, lang.Final):
    _ROLE_TAG: ta.ClassVar[str] = 'function'

    content: str | None
    name: str
