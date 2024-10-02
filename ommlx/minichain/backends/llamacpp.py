import os.path
import typing as ta

from omlish import check
from omlish import lang

from ..chat import AiMessage
from ..chat import ChatModel
from ..chat import ChatRequest
from ..chat import ChatResponse
from ..chat import Message
from ..chat import SystemMessage
from ..chat import ToolExecutionResultMessage
from ..chat import UserMessage
from ..content import Text
from ..models import Request
from ..models import Response
from ..prompts import Prompt
from ..prompts import PromptModel
from ..prompts import PromptRequest
from ..prompts import PromptResponse


if ta.TYPE_CHECKING:
    import llama_cpp
else:
    llama_cpp = lang.proxy_import('llama_cpp')


class LlamacppPromptModel(PromptModel):
    model_path = os.path.join(
        os.path.expanduser('~/.cache/huggingface/hub'),
        'models--QuantFactory--Meta-Llama-3-8B-GGUF',
        'snapshots',
        '1ca85c857dce892b673b988ad0aa83f2cb1bbd19',
        'Meta-Llama-3-8B.Q8_0.gguf',
    )

    def generate(self, request: PromptRequest) -> PromptResponse:
        llm = llama_cpp.Llama(
            model_path=self.model_path,
        )

        output = llm.create_completion(
            request.v.s,
            max_tokens=1024,
            stop=['\n'],
        )

        return PromptResponse(v=output['choices'][0]['text'])  # type: ignore


class LlamacppChatModel(ChatModel):
    model_path = os.path.join(
        os.path.expanduser('~/.cache/huggingface/hub'),
        'models--TheBloke--Llama-2-7B-Chat-GGUF',
        'snapshots',
        '191239b3e26b2882fb562ffccdd1cf0f65402adb',
        'llama-2-7b-chat.Q5_0.gguf',
    )

    ROLES_MAP: ta.ClassVar[ta.Mapping[type[Message], str]] = {
        SystemMessage: 'system',
        UserMessage: 'user',
        AiMessage: 'assistant',
        ToolExecutionResultMessage: 'tool',
    }

    def _get_msg_content(self, m: Message) -> str:
        if isinstance(m, (SystemMessage, AiMessage)):
            return m.s

        elif isinstance(m, UserMessage):
            return ''.join(check.isinstance(c, Text).s for c in m.content)

        else:
            raise TypeError(m)

    def generate(self, request: ChatRequest) -> ChatResponse:
        llm = llama_cpp.Llama(
            model_path=self.model_path,
        )

        output = llm.create_chat_completion(
            messages=[  # noqa
                dict(  # type: ignore
                    role=self.ROLES_MAP[type(m)],
                    content=self._get_msg_content(m),
                )
                for m in request.v
            ],
            max_tokens=1024,
            # stop=['\n'],
        )

        return ChatResponse(v=AiMessage(output['choices'][0]['message']['content']))  # type: ignore
