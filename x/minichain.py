import abc
import enum
import dataclasses as dc
import typing as ta
import os.path

import yaml


T = ta.TypeVar('T')
U = ta.TypeVar('U')


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


class Invokable(abc.ABC, ta.Generic[T, U]):
    @abc.abstractmethod
    def invoke(self, arg: T) -> U:
        raise NotImplementedError


@dc.dataclass(frozen=True)
class ChainedInvokable(Invokable):
    children: ta.Sequence[Invokable]

    def invoke(self, arg: ta.Any) -> ta.Any:
        for c in self.children:
            arg = c.invoke(arg)
        return arg


##


class ChatOpenAi(Invokable):
    def __init__(self, model: str) -> None:
        super().__init__()
        self._mode = model

    def invoke(self, arg: ta.Any) -> ta.Any:
        raise NotImplementedError


##


class StrOutputParser(Invokable):
    def invoke(self, arg: ta.Any) -> ta.Any:
        raise NotImplementedError


##


def load_secrets() -> None:
    with open(os.path.expanduser('~/Dropbox/.dotfiles/secrets.yml')) as f:
        dct = yaml.safe_load(f)
    os.environ['OPENAI_API_KEY'] = dct['openai_api_key']
    os.environ['TAVILY_API_KEY'] = dct['tavily_api_key']


def _main() -> None:
    load_secrets()

    #

    model = ChatOpenAi(model='gpt-4')
    parser = StrOutputParser()
    chain = ChainedInvokable([
        model,
        parser,
    ])

    #

    messages = [
        SystemMessage('Translate the following from English into Italian'),
        HumanMessage('hi!'),
    ]

    result = chain.invoke(messages)
    print(result)


if __name__ == '__main__':
    _main()
