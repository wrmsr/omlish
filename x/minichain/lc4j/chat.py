import abc
import dataclasses as dc
import enum
import typing as ta

from omlish import collections as col
from omlish import lang


T = ta.TypeVar('T')
U = ta.TypeVar('U')


#


class Message(lang.Abstract, lang.Sealed):
    pass


class SystemMessage(Message, lang.Final):
    s: str


class UserMessage(Message, lang.Final):
    content: ta.Sequence[Content]
    name: str | None = None


class AiMessage(Message, lang.Final):
    s: str
    tool_execution_requests: ta.Sequence['ToolExecutionRequest'] | None = None


class ToolExecutionResultMessage(Message, lang.Final):
    id: str
    tool_name: str
    s: str


Chat: ta.TypeAlias = ta.Sequence[Message]


