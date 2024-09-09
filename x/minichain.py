import abc
import enum
import dataclasses as dc
import typing as ta


##


class MessageSource(enum.Enum):
    SYSTEM = enum.auto()
    HUMAN = enum.auto()
    AI = enum.auto()


@dc.dataclass(frozen=True)
class Message(abc.ABC):  # noqa
    content: str

    source: ta.ClassVar[MessageSource]


@dc.dataclass(frozen=True)
class SystemMessage(Message):
    source = MessageSource.SYSTEM


@dc.dataclass(frozen=True)
class HumanMessage(Message):
    source = MessageSource.HUMAN


@dc.dataclass(frozen=True)
class AiMessage(Message):
    source = MessageSource.AI


##


