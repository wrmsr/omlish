import abc
import dataclasses as dc
import datetime
import enum
import os.path
import typing as ta

from omlish import lang


if ta.TYPE_CHECKING:
    import llama_cpp
    import openai

else:
    llama_cpp = lang.proxy_import('llama_cpp')
    openai = lang.proxy_import('openai')


T = ta.TypeVar('T')


##


class ChatRole(enum.Enum):
    SYSTEM = enum.auto()
    USER = enum.auto()
    ASSISTANT = enum.auto()


@dc.dataclass(frozen=True)
class ChatMessage:
    role: ChatRole
    text: str

    created_at: datetime.datetime = dc.field(default_factory=datetime.datetime.now)


@dc.dataclass(frozen=True)
class Chat:
    name: str | None = None

    created_at: datetime.datetime = dc.field(default_factory=datetime.datetime.now)
    updated_at: datetime.datetime = dc.field(default_factory=datetime.datetime.now)

    messages: ta.Sequence[ChatMessage] = ()


##


class ChatLlm(abc.ABC):
    @abc.abstractmethod
    def get_completion(self, messages: ta.Sequence[ChatMessage]) -> str:
        raise NotImplementedError


class OpenaiChatLlm(ChatLlm):
    model = 'gpt-4o'

    ROLES_MAP: ta.ClassVar[ta.Mapping[ChatRole, str]] = {
        ChatRole.SYSTEM: 'system',
        ChatRole.USER: 'user',
        ChatRole.ASSISTANT: 'assistant',
    }

    def get_completion(self, messages: ta.Sequence[ChatMessage]) -> str:
        response = openai.chat.completions.create(  # noqa
            model=self.model,
            messages=[
                dict(
                    role=self.ROLES_MAP[m.role],
                    content=m.text,
                )
                for m in messages
            ],
            temperature=0,
            max_tokens=1024,
            top_p=1,
            frequency_penalty=0.0,
            presence_penalty=0.0,
            stream=False,
        )

        return response.choices[0].message.content


class LlamacppChatLlm(ChatLlm):
    model_path = os.path.join(
        os.path.expanduser('~/.cache/huggingface/hub'),
        'models--TheBloke--Llama-2-7B-Chat-GGUF',
        'snapshots',
        '191239b3e26b2882fb562ffccdd1cf0f65402adb',
        'llama-2-7b-chat.Q5_0.gguf',
    )

    ROLES_MAP: ta.ClassVar[ta.Mapping[ChatRole, str]] = {
        ChatRole.SYSTEM: 'system',
        ChatRole.USER: 'user',
        ChatRole.ASSISTANT: 'assistant',
    }

    def get_completion(self, messages: ta.Sequence[ChatMessage]) -> str:
        llm = llama_cpp.Llama(
            model_path=self.model_path,
        )

        output = llm.create_chat_completion(
            messages=[  # noqa
                dict(
                    role=self.ROLES_MAP[m.role],
                    content=m.text,
                )
                for m in messages
            ],
            max_tokens=1024,
            # stop=["\n"],
        )

        return output['choices'][0]['message']['content']
