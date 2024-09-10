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


class ChatCompleter(abc.ABC):
    @abc.abstractmethod
    def complete_chat(self, messages: Messages) -> AiMessage:
        raise NotImplementedError


#


class OpenaiChatCompleter(ChatCompleter, lang.Final):
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

    def complete_chat(self, msgs: Messages) -> AiMessage:
        payload = {
            'messages': [self._build_message_payload(msg) for msg in msgs],
            'model': self._model,
            'n': 1,
            'stream': False,
            'temperature': 0.7,
        }

        response = self._client.chat.completions.create(**payload)
        choice = check.single(response.choices)
        return AiMessage(choice.message.content)


##


class MessageParser(abc.ABC, ta.Generic[T]):
    @abc.abstractmethod
    def parse_message(self, msg: Message) -> T:
        raise NotImplementedError


#


class StrMessageParser(MessageParser[str], lang.Final):
    def parse_message(self, msg: Message) -> str:
        return msg.content


##


@dc.dataclass(frozen=True)
class EnvRef:
    key: str


MessageTemplatable: ta.TypeAlias = ta.Union[
    Message,
    ta.Iterable[Message],
    EnvRef,
]


@dc.dataclass(frozen=True)
class MessageTemplater:
    body: ta.Sequence[MessageTemplatable]

    def template_messages(self, env: StrMap) -> Messages:
        out: list[Message] = []
        stk: list[MessageTemplatable] = list(reversed(self.body))
        while stk:
            b = stk.pop()

            if isinstance(b, Message):
                out.append(dc.replace(b, content=b.content.format(**env)))

            elif isinstance(b, ta.Iterable):
                stk.extend(reversed(b))

            elif isinstance(b, EnvRef):
                stk.extend(reversed(env[b.key]))

            else:
                raise TypeError(b)

        return out


##


def _run_2_chatbot(client: openai.OpenAI) -> None:
    chat_completer = OpenaiChatCompleter(client, 'gpt-3.5-turbo')

    result = chat_completer.complete_chat([HumanMessage(content="Hi! I'm Bob")])
    print(result)

    #

    result = chat_completer.complete_chat([HumanMessage(content="What's my name?")])
    print(result)

    #

    result = chat_completer.complete_chat([
        HumanMessage(content="Hi! I'm Bob"),
        AiMessage(content='Hello Bob! How can I assist you today?'),
        HumanMessage(content="What's my name?"),
    ])
    print(result)


#


def _run_1_chain(client: openai.OpenAI) -> None:
    chat_completer = OpenaiChatCompleter(client, 'gpt-4')
    message_parser = StrMessageParser()

    #

    messages = [
        SystemMessage('Translate the following from English into Italian'),
        HumanMessage('hi!'),
    ]

    result = message_parser.parse_message(
        chat_completer.complete_chat(
            messages,
        ),
    )
    print(result)

    #

    message_templater = MessageTemplater([
        SystemMessage('Translate the following from English into {language}'),
        HumanMessage('{text}'),
    ])

    result = message_parser.parse_message(
        chat_completer.complete_chat(
            message_templater.template_messages({
                'language': 'Italian',
                'text': 'hi!',
            }),
        ),
    )
    print(result)


#


def _run(es: contextlib.ExitStack) -> None:
    client = es.enter_context(openai.OpenAI(
        api_key=os.environ['OPENAI_API_KEY'],
    ))

    #

    _run_1_chain(client)
    _run_2_chatbot(client)


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
