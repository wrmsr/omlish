import contextlib
import os.path
import typing as ta

from omlish import check
from omlish import lang

from ..chat.choices import AiChoice
from ..chat.messages import AiMessage
from ..chat.messages import Message
from ..chat.messages import SystemMessage
from ..chat.messages import ToolExecResultMessage
from ..chat.messages import UserMessage
from ..chat.services import ChatRequest
from ..chat.services import ChatResponse
from ..chat.services import ChatService
from ..prompt import PromptRequest
from ..prompt import PromptResponse
from ..prompt import PromptService


if ta.TYPE_CHECKING:
    import llama_cpp

    from ... import llamacpp as lcu

else:
    llama_cpp = lang.proxy_import('llama_cpp')

    lcu = lang.proxy_import('...llamacpp', __package__)


##


# @omlish-manifest ommlx.minichain.backends.manifests.BackendManifest(name='llamacpp', type='PromptService')
class LlamacppPromptService(PromptService):
    # hf.hf_hub_download(
    #   revision='1ca85c857dce892b673b988ad0aa83f2cb1bbd19',
    #   repo_id='QuantFactory/Meta-Llama-3-8B-GGUF',
    #   filename='Meta-Llama-3-8B.Q8_0.gguf',
    # )
    model_path = os.path.join(
        os.path.expanduser('~/.cache/huggingface/hub'),
        'models--QuantFactory--Meta-Llama-3-8B-GGUF',
        'snapshots',
        '1ca85c857dce892b673b988ad0aa83f2cb1bbd19',
        'Meta-Llama-3-8B.Q8_0.gguf',
    )

    def invoke(self, request: PromptRequest) -> PromptResponse:
        lcu.install_logging_hook()

        llm = llama_cpp.Llama(
            model_path=self.model_path,
        )

        output = llm.create_completion(
            request.prompt,
            max_tokens=1024,
            stop=['\n'],
        )

        return PromptResponse(output['choices'][0]['text'])  # type: ignore


# @omlish-manifest ommlx.minichain.backends.manifests.BackendManifest(name='llamacpp', type='ChatService')
class LlamacppChatService(ChatService):
    model_path = os.path.join(
        os.path.expanduser('~/.cache/huggingface/hub'),
        # 'models--meta-llama--Llama-3.2-3B-Instruct/snapshots/0cb88a4f764b7a12671c53f0838cd831a0843b95/llama-2-7b-chat.Q5_0.gguf',  # noqa
        # 'models--QuantFactory--Meta-Llama-3-8B-GGUF/snapshots/1ca85c857dce892b673b988ad0aa83f2cb1bbd19/Meta-Llama-3-8B.Q8_0.gguf',  # noqa
        'models--TheBloke--TinyLlama-1.1B-Chat-v1.0-GGUF/snapshots/52e7645ba7c309695bec7ac98f4f005b139cf465/tinyllama-1.1b-chat-v1.0.Q6_K.gguf',  # noqa
    )

    ROLES_MAP: ta.ClassVar[ta.Mapping[type[Message], str]] = {
        SystemMessage: 'system',
        UserMessage: 'user',
        AiMessage: 'assistant',
        ToolExecResultMessage: 'tool',
    }

    @classmethod
    def _get_msg_content(cls, m: Message) -> str | None:
        if isinstance(m, (SystemMessage, AiMessage)):
            return m.s

        elif isinstance(m, UserMessage):
            return check.isinstance(m.c, str)

        else:
            raise TypeError(m)

    def invoke(self, request: ChatRequest) -> ChatResponse:
        lcu.install_logging_hook()

        with contextlib.ExitStack() as es:
            llm = es.enter_context(contextlib.closing(llama_cpp.Llama(
                model_path=self.model_path,
                verbose=False,
            )))

            output = llm.create_chat_completion(
                messages=[  # noqa
                    dict(  # type: ignore
                        role=self.ROLES_MAP[type(m)],
                        content=self._get_msg_content(m),
                    )
                    for m in request.chat
                ],
                max_tokens=1024,
                # stop=['\n'],
            )

            return ChatResponse([
                AiChoice(AiMessage(c['message']['content']))  # noqa
                for c in output['choices']  # type: ignore
            ])
