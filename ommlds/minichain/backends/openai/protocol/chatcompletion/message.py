# ruff: noqa: UP007
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


class UserChatCompletionMessage(ta.TypedDict, total=False):
    content: ta.Required[str | ta.Iterable[ChatCompletionContentPart]]
    role: ta.Required[ta.Literal['user']]
    name: str


#


class AssistantChatCompletionMessageAudio(ta.TypedDict, total=False):
    id: ta.Required[str]


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


class ToolChatCompletionMessage(ta.TypedDict, total=False):
    content: ta.Required[str | ta.Iterable[TextChatCompletionContentPart]]
    role: ta.Required[ta.Literal['tool']]
    tool_call_id: ta.Required[str]


#


class FunctionChatCompletionMessage(ta.TypedDict, total=False):
    content: ta.Required[str | None]
    name: ta.Required[str]
    role: ta.Required[ta.Literal['function']]


#


ChatCompletionMessage: ta.TypeAlias = ta.Union[
    DeveloperChatCompletionMessage,
    SystemChatCompletionMessage,
    UserChatCompletionMessage,
    AssistantChatCompletionMessage,
    ToolChatCompletionMessage,
    FunctionChatCompletionMessage,
]
