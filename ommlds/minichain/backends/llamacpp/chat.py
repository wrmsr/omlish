import contextlib
import os.path
import typing as ta

import llama_cpp as lcc

from omlish import check
from omlish import lang
from omlish import typedvalues as tv

from ....backends import llamacpp as lcu
from ...chat.choices import AiChoice
from ...chat.messages import AiMessage
from ...chat.services import ChatRequest
from ...chat.services import ChatResponse
from ...chat.services import ChatService
from ...chat.tools import Tool
from ...completion import CompletionRequestOption
from ...configs import Config
from ...configs import consume_configs
from ...llms.services import LlmRequestOption
from ...llms.services import MaxTokens
from ...llms.services import Temperature
from ...standard import ModelPath
from ...tools.types import PrimitiveToolDtype
from .format import ROLES_MAP
from .format import get_msg_content


##


# @omlish-manifest ommlds.minichain.backends.manifests.BackendManifest(name='llamacpp', type='ChatService')
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

    _OPTION_KWARG_NAMES_MAP: ta.ClassVar[ta.Mapping[str, type[CompletionRequestOption | LlmRequestOption]]] = dict(
        max_tokens=MaxTokens,
        temperatur=Temperature,
    )

    def invoke(self, request: ChatRequest) -> ChatResponse:
        kwargs: dict = dict(
            # temperature=0,
            max_tokens=1024,
            # stop=['\n'],
        )

        tools_by_name: dict[str, dict] = {}

        with tv.TypedValues(*request.options).consume() as oc:
            kwargs.update(oc.pop_scalar_kwargs(**self._OPTION_KWARG_NAMES_MAP))

            for t in oc.pop(Tool, []):
                if t.spec.name in tools_by_name:
                    raise NameError(t.spec.name)

                tools_by_name[t.spec.name] = dict(
                    name=t.spec.name,

                    **lang.opt_kw(description=t.spec.desc),

                    parameters=dict(
                        type='object',
                        properties={
                            tp.name: dict(
                                type=check.isinstance(tp.type, PrimitiveToolDtype).type,
                                **lang.opt_kw(description=tp.desc),
                            )
                            for tp in t.spec.params or []
                        },
                    ),
                )

        if tools_by_name:
            kwargs['tools'] = list(tools_by_name.values())

        lcu.install_logging_hook()

        with contextlib.ExitStack() as es:
            llm = es.enter_context(contextlib.closing(lcc.Llama(
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
                **kwargs,
            )

            return ChatResponse([
                AiChoice(AiMessage(c['message']['content']))  # noqa
                for c in output['choices']  # type: ignore
            ])
