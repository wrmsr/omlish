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


class Invokable(abc.ABC):
    def invoke(self, *args: ta.Any, **kwargs: ta.Any) -> ta.Any:
        raise NotImplementedError


##


def _main() -> None:
    pass


if __name__ == '__main__':
    _main()
