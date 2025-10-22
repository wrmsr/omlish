import contextlib
import os.path
import typing as ta

import llama_cpp as lcc

from omlish import check
from omlish import lang
from omlish import typedvalues as tv

from .....backends import llamacpp as lcu
from ....chat.choices.services import ChatChoicesRequest
from ....chat.choices.services import ChatChoicesResponse
from ....chat.choices.services import static_check_is_chat_choices_service
from ....chat.choices.types import AiChoice
from ....chat.choices.types import ChatChoicesOptions
from ....chat.messages import AiMessage
from ....chat.messages import ToolUseMessage
from ....chat.messages import ToolUseResultMessage
from ....chat.tools.types import Tool
from ....configs import Config
from ....llms.types import MaxTokens
from ....llms.types import Temperature
from ....models.configs import ModelPath
from ....tools.types import PrimitiveToolDtype
from .format import ROLES_MAP
from .format import get_msg_content


##


# @omlish-manifest $.minichain.backends.strings.manifests.BackendStringsManifest(
#     ['ChatChoicesService'],
#     'llamacpp',
# )


##


# @omlish-manifest $.minichain.registries.manifests.RegistryManifest(
#     name='llamacpp',
#     type='ChatChoicesService',
# )
@static_check_is_chat_choices_service
class LlamacppChatChoicesService:
    DEFAULT_MODEL_PATH: ta.ClassVar[str] = os.path.join(
        os.path.expanduser('~/.cache/huggingface/hub'),
        # 'models--meta-llama--Llama-3.2-3B-Instruct/snapshots/0cb88a4f764b7a12671c53f0838cd831a0843b95/llama-2-7b-chat.Q5_0.gguf',  # noqa
        # 'models--QuantFactory--Meta-Llama-3-8B-GGUF/snapshots/1ca85c857dce892b673b988ad0aa83f2cb1bbd19/Meta-Llama-3-8B.Q8_0.gguf',  # noqa
        'models--TheBloke--TinyLlama-1.1B-Chat-v1.0-GGUF/snapshots/52e7645ba7c309695bec7ac98f4f005b139cf465/tinyllama-1.1b-chat-v1.0.Q6_K.gguf',  # noqa
        # 'models--mradermacher--watt-tool-70B-GGUF/snapshots/0825425bbf023ef7bc96b94fdf1ec3f39eb869ff/watt-tool-70B.Q5_K_M.gguf',  # noqa
    )

    def __init__(self, *configs: Config) -> None:
        super().__init__()

        with tv.consume(*configs) as cc:
            self._model_path = cc.pop(ModelPath(self.DEFAULT_MODEL_PATH))

    _OPTION_KWARG_NAMES_MAP: ta.ClassVar[ta.Mapping[str, type[ChatChoicesOptions]]] = dict(
        max_tokens=MaxTokens,
        temperatur=Temperature,
    )

    async def invoke(self, request: ChatChoicesRequest) -> ChatChoicesResponse:
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

                tools_by_name[check.non_empty_str(t.spec.name)] = dict(
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

            ims: list = []
            for rm in request.v:
                if isinstance(rm, ToolUseResultMessage):
                    ims.append(dict(
                        role='tool',
                        **(dict(id=rm.tur.id) if rm.tur.id is not None else {}),
                        name=rm.tur.name,
                        content=check.isinstance(rm.tur.c, str),
                    ))

                elif isinstance(rm, AiMessage):
                    ims.append(dict(
                        role=ROLES_MAP[type(rm)],
                        **(dict(content=mc) if (mc := get_msg_content(rm)) is not None else {}),
                    ))

                elif isinstance(rm, ToolUseMessage):
                    ims.append(dict(
                        role=ROLES_MAP[type(rm)],
                        content='',
                        tool_calls=[dict(
                            id=check.not_none(rm.tu.id),
                            type='function',
                            function=dict(
                                name=rm.tu.name,
                                arguments=check.isinstance(rm.tu.raw_args, str),
                            ),
                        )],
                    ))

                else:
                    ims.append(dict(
                        role=ROLES_MAP[type(rm)],
                        **(dict(content=mc) if (mc := get_msg_content(rm)) is not None else {}),
                    ))

            output = llm.create_chat_completion(
                messages=ims,
                **kwargs,
            )

            out: list[AiChoice] = []
            for c in ta.cast(ta.Any, output)['choices']:
                m = c['message']
                out.append(AiChoice([AiMessage(m['content'])]))

            return ChatChoicesResponse(out)
