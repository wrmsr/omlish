# ruff: noqa: UP007 UP045
import typing as ta

from .contentpart import ChatCompletionContentPart
from .contentpart import RefusalChatCompletionContentPart
from .contentpart import TextChatCompletionContentPart


##


class DeveloperChatCompletionMessage(ta.TypedDict):
    content: str | ta.Iterable[TextChatCompletionContentPart]
    role: ta.Literal['developer']
    name: ta.NotRequired[str]


#


class SystemChatCompletionMessage(ta.TypedDict):
    content: str | ta.Iterable[TextChatCompletionContentPart]
    role: ta.Literal['system']
    name: ta.NotRequired[str]


#


class UserChatCompletionMessage(ta.TypedDict):
    content: str | ta.Iterable[ChatCompletionContentPart]
    role: ta.Literal['user']
    name: ta.NotRequired[str]


#


class AssistantChatCompletionMessageAudio(ta.TypedDict):
    id: str


class AssistantChatCompletionMessageToolCallFunction(ta.TypedDict):
    arguments: str
    name: str


class AssistantChatCompletionMessageToolCall(ta.TypedDict):
    id: str
    function: AssistantChatCompletionMessageToolCallFunction
    type: ta.Literal['function']


class AssistantChatCompletionMessage(ta.TypedDict, total=False):
    role: ta.Required[ta.Literal['assistant']]
    audio: AssistantChatCompletionMessageAudio
    content: str | ta.Iterable[TextChatCompletionContentPart | RefusalChatCompletionContentPart]
    name: str
    refusal: str
    tool_calls: ta.Iterable[AssistantChatCompletionMessageToolCall]


#


class ToolChatCompletionMessage(ta.TypedDict):
    content: str | ta.Iterable[TextChatCompletionContentPart]
    role: ta.Literal['tool']
    tool_call_id: str


#


class FunctionChatCompletionMessage(ta.TypedDict):
    content: str | None
    name: str
    role: ta.Literal['function']


#


ChatCompletionMessage: ta.TypeAlias = ta.Union[
    DeveloperChatCompletionMessage,
    SystemChatCompletionMessage,
    UserChatCompletionMessage,
    AssistantChatCompletionMessage,
    ToolChatCompletionMessage,
    FunctionChatCompletionMessage,
]
