import contextlib
import os.path
import typing as ta

from omlish import lang

from ...chat.choices import AiChoice
from ...chat.messages import AiMessage
from ...chat.services import ChatRequest
from ...chat.services import ChatResponse
from ...chat.services import ChatService
from ...configs import Config
from ...configs import consume_configs
from ...standard import ModelPath
from .format import ROLES_MAP
from .format import get_msg_content


if ta.TYPE_CHECKING:
    import llama_cpp

    from ....backends import llamacpp as lcu

else:
    llama_cpp = lang.proxy_import('llama_cpp')

    lcu = lang.proxy_import('....backends.llamacpp', __package__)


##


# @omlish-manifest ommlx.minichain.backends.manifests.BackendManifest(name='llamacpp', type='ChatService')
class LlamacppChatService(ChatService):
    DEFAULT_MODEL_PATH: ta.ClassVar[str] = os.path.join(
        os.path.expanduser('~/.cache/huggingface/hub'),
        # 'models--meta-llama--Llama-3.2-3B-Instruct/snapshots/0cb88a4f764b7a12671c53f0838cd831a0843b95/llama-2-7b-chat.Q5_0.gguf',  # noqa
        # 'models--QuantFactory--Meta-Llama-3-8B-GGUF/snapshots/1ca85c857dce892b673b988ad0aa83f2cb1bbd19/Meta-Llama-3-8B.Q8_0.gguf',  # noqa
        'models--TheBloke--TinyLlama-1.1B-Chat-v1.0-GGUF/snapshots/52e7645ba7c309695bec7ac98f4f005b139cf465/tinyllama-1.1b-chat-v1.0.Q6_K.gguf',  # noqa
    )

    def __init__(self, *configs: Config) -> None:
        super().__init__()

        with consume_configs(*configs) as cc:
            self._model_path = cc.pop(ModelPath(self.DEFAULT_MODEL_PATH))

    def invoke(self, request: ChatRequest) -> ChatResponse:
        lcu.install_logging_hook()

        with contextlib.ExitStack() as es:
            llm = es.enter_context(contextlib.closing(llama_cpp.Llama(
                model_path=self._model_path.v,
                verbose=False,
            )))

            output = llm.create_chat_completion(
                messages=[  # noqa
                    dict(  # type: ignore
                        role=ROLES_MAP[type(m)],
                        content=get_msg_content(m),
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
