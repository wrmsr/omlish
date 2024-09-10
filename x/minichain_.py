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


class Invokable(lang.Abstract, ta.Generic[T, U]):
    @abc.abstractmethod
    def invoke(self, arg: T) -> U:
        raise NotImplementedError

    def __call__(self, arg: T) -> U:
        return self.invoke(arg)


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

    def invoke(self, msgs: Messages) -> AiMessage:  # type: ignore
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


class StrOutputParser(Invokable, lang.Final):
    def invoke(self, msg: Message) -> str:  # type: ignore
        return msg.content


##


@dc.dataclass(frozen=True)
class MessagesPlaceholder:
    var: str


@dc.dataclass(frozen=True)
class ChatPromptTemplate(Invokable, lang.Final):
    body: ta.Sequence[Message | MessagesPlaceholder]

    def invoke(self, env: StrMap) -> Messages:
        stk: list[Message | MessagesPlaceholder] = list(reversed(self.body))
        out: list[Message] = []
        while stk:
            b = stk.pop()
            if isinstance(b, Message):
                out.append(dc.replace(b, content=b.content.format(**env)))
            elif isinstance(b, MessagesPlaceholder):
                stk.extend(reversed(env[b.var]))
            else:
                raise TypeError(b)
        return out


##


@dc.dataclass(frozen=True)
class ChatSession:
    messages: Messages


@dc.dataclass(frozen=True)
class ChatSessionStore:
    store: dict[str, ChatSession] = dc.field(default_factory=dict)

    def get(self, session_id: str) -> ChatSession | None:
        return self.store.get(session_id)

    def put(self, session_id: str, session: ChatSession) -> None:
        self.store[session_id] = session


@dc.dataclass(frozen=True)
class ChatSessionAddition:
    messages: Messages
    session_id: str | None = None


@dc.dataclass(frozen=True)
class MessageHistoryChat(Invokable):
    store: ChatSessionStore

    def invoke(self, new: ChatSessionAddition) -> Messages:
        if new.session_id is None:
            return new.messages

        session = self.store.get(new.session_id)
        if session is None:
            return new.messages

        return [
            *session.messages,
            *new.messages,
        ]


@dc.dataclass(frozen=True)
class UpdatingMessageHistoryChat(Invokable):
    child: Invokable
    store: ChatSessionStore

    def invoke(self, new: ChatSessionAddition) -> Messages:
        in_messages = MessageHistoryChat(self.store).invoke(new)

        out_message = self.child(in_messages)

        out_messages = [
            *in_messages,
            out_message,
        ]

        if new.session_id is not None:
            self.store.put(new.session_id, ChatSession(out_messages))

        return out_messages


##


def _run_2_chatbot(client: openai.OpenAI) -> None:
    model = ChatOpenAi(client, 'gpt-3.5-turbo')

    result = model([HumanMessage(content="Hi! I'm Bob")])
    print(result)

    #

    result = model([HumanMessage(content="What's my name?")])
    print(result)

    #

    result = model([
        HumanMessage(content="Hi! I'm Bob"),
        AiMessage(content='Hello Bob! How can I assist you today?'),
        HumanMessage(content="What's my name?"),
    ])
    print(result)

    #

    chat_sessions = ChatSessionStore()

    with_message_history = UpdatingMessageHistoryChat(
        model,
        chat_sessions,
    )

    response = with_message_history.invoke(ChatSessionAddition(
        [HumanMessage(content="Hi! I'm Bob")],
        session_id='abc2',
    ))
    print(response)

    #

    response = with_message_history.invoke(ChatSessionAddition(
        [HumanMessage(content="What's my name?")],
        session_id='abc2',
    ))
    print(response)

    #

    prompt = ChatPromptTemplate([
        SystemMessage("You are a helpful assistant. Answer all questions to the best of your ability in {language}."),
        MessagesPlaceholder("messages"),
    ])

    chain = ChainedInvokable([
        prompt,
        model,
    ])

    #

    response = chain.invoke({
        "messages": [HumanMessage(content="hi! I'm bob")],
        "language": "Spanish"
    })
    print(response)

    #

    with_message_history = UpdatingMessageHistoryChat(
        model,
        chat_sessions,
    )

    # with_message_history = RunnableWithMessageHistory(
    #     chain,
    #     get_session_history,
    #     input_messages_key="messages",
    # )

    config = {"configurable": {"session_id": "abc11"}}

    response = with_message_history.invoke({
        "messages": [HumanMessage(content="hi! I'm todd")],
        "language": "Spanish",
    }, config=config)
    print(response)

    response = with_message_history.invoke({
        "messages": [HumanMessage(content="whats my name?")],
        "language": "Spanish",
    }, config=config)
    print(response)


#


def _run_1_chain(client: openai.OpenAI) -> None:
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


def _run(es: contextlib.ExitStack) -> None:
    client = es.enter_context(openai.OpenAI(
        api_key=os.environ['OPENAI_API_KEY'],
    ))

    #

    # _run_1_chain(client)
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
