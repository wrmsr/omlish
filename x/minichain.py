import abc
import contextlib
import dataclasses as dc
import enum
import os.path
import typing as ta

import openai
import yaml

from omlish import check
from omlish import lang


T = ta.TypeVar('T')
U = ta.TypeVar('U')

StrMap: ta.TypeAlias = ta.Mapping[str, ta.Any]

Messages: ta.TypeAlias = ta.Sequence['Message']


##


class MessageRole(enum.Enum):
    SYSTEM = enum.auto()
    HUMAN = enum.auto()
    AI = enum.auto()


@dc.dataclass(frozen=True)
class Message(lang.Abstract):
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


##


@dc.dataclass(frozen=True)
class Generation(lang.Final):
    text: str


##


class Invokable(lang.Abstract, ta.Generic[T, U]):
    @abc.abstractmethod
    def invoke(self, arg: T) -> U:
        raise NotImplementedError


@dc.dataclass(frozen=True)
class ChainedInvokable(Invokable, lang.Final):
    children: ta.Sequence[Invokable]

    def invoke(self, arg: ta.Any) -> ta.Any:
        for c in self.children:
            arg = c.invoke(arg)
        return arg


##


class ChatOpenAi(Invokable, lang.Final):
    def __init__(
            self,
            client: openai.OpenAI,
            model: str,
    ) -> None:
        super().__init__()
        self._client = client
        self._model = model

    _ROLE_MAP: ta.ClassVar[ta.Mapping[MessageRole, str]] = {
        MessageRole.SYSTEM: 'system',
        MessageRole.HUMAN: 'user',
        MessageRole.AI: 'assistant',
    }

    def _build_message_payload(self, msg: Message) -> StrMap:
        return dict(
            role=self._ROLE_MAP[msg.role],
            content=msg.content,
        )

    def invoke(self, msgs: Messages) -> Generation:  # type: ignore
        payload = {
            'messages': [self._build_message_payload(msg) for msg in msgs],
            'model': self._model,
            'n': 1,
            'stream': False,
            'temperature': 0.7,
        }

        response = self._client.chat.completions.create(**payload)
        choice = check.single(response.choices)
        return Generation(choice.message.content)


##


class StrOutputParser(Invokable, lang.Final):
    def invoke(self, gen: Generation) -> str:  # type: ignore
        return gen.text


##


@dc.dataclass(frozen=True)
class ChatPromptTemplate(Invokable, lang.Final):
    msgs: Messages

    def invoke(self, env: StrMap) -> Messages:
        out: list[Message] = []
        for m in self.msgs:
            out.append(dc.replace(m, content=m.content.format(**env)))
        return out


##


def _run(es: contextlib.ExitStack) -> None:
    client = es.enter_context(openai.OpenAI(
        api_key=os.environ['OPENAI_API_KEY'],
    ))

    #

    model = ChatOpenAi(client, 'gpt-4')
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

    #

    prompt_template = ChatPromptTemplate([
        SystemMessage('Translate the following from English into {language}'),
        HumanMessage('{text}'),
    ])

    chain = ChainedInvokable([
        prompt_template,
        chain,
    ])

    result = chain.invoke({'language': 'Italian', 'text': 'hi!'})
    print(result)


#


def _load_secrets() -> None:
    with open(os.path.expanduser('~/Dropbox/.dotfiles/secrets.yml')) as f:
        dct = yaml.safe_load(f)
    os.environ['OPENAI_API_KEY'] = dct['openai_api_key']
    os.environ['TAVILY_API_KEY'] = dct['tavily_api_key']


def _main() -> None:
    _load_secrets()

    with contextlib.ExitStack() as es:
        _run(es)


if __name__ == '__main__':
    _main()
