import dataclasses as dc
import enum
import typing as ta

from omlish import lang


Messages: ta.TypeAlias = ta.Sequence['Message']


##


class MessageRole(enum.Enum):
    SYSTEM = enum.auto()
    HUMAN = enum.auto()
    AI = enum.auto()


@dc.dataclass(frozen=True)
class Message(lang.Sealed, lang.Abstract):
    content: str

    role: ta.ClassVar[MessageRole]


@dc.dataclass(frozen=True)
class SystemMessage(Message, lang.Final):
    role = MessageRole.SYSTEM


@dc.dataclass(frozen=True)
class HumanMessage(Message, lang.Final):
    role = MessageRole.HUMAN


@dc.dataclass(frozen=True)
class AiMessage(Message, lang.Final):
    role = MessageRole.AI
