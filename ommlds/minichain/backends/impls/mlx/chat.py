import typing as ta

from omlish import check
from omlish import lang
from omlish import typedvalues as tv

from .....backends import mlx as mlxu
from ....chat.choices.services import ChatChoicesRequest
from ....chat.choices.services import ChatChoicesResponse
from ....chat.choices.services import static_check_is_chat_choices_service
from ....chat.choices.types import AiChoice
from ....chat.choices.types import ChatChoicesOptions
from ....chat.messages import AiMessage
from ....chat.messages import Message
from ....chat.messages import SystemMessage
from ....chat.messages import UserMessage
from ....configs import Config
from ....llms.types import MaxTokens
from ....models.configs import ModelPath
from ....models.configs import ModelRepo
from ....models.configs import ModelSpecifier
from ....standard import DefaultOptions


##


# @omlish-manifest $.minichain.backends.strings.manifests.BackendStringsManifest(
#     ['ChatChoicesService'],
#     'mlx',
# )


##


# @omlish-manifest $.minichain.registries.manifests.RegistryManifest(
#     name='mlx',
#     type='ChatChoicesService',
# )
@static_check_is_chat_choices_service
class MlxChatChoicesService(lang.ExitStacked):
    DEFAULT_MODEL: ta.ClassVar[ModelSpecifier] = (
        # 'mlx-community/DeepSeek-Coder-V2-Lite-Instruct-8bit'
        # 'mlx-community/Llama-3.3-70B-Instruct-4bit'
        # 'mlx-community/Llama-3.3-70B-Instruct-6bit'
        ModelRepo('mlx-community', 'Llama-3.3-70B-Instruct-8bit')
        # 'mlx-community/Mistral-Small-3.1-Text-24B-Instruct-2503-8bit'
        # 'mlx-community/Mixtral-8x7B-Instruct-v0.1'
        # 'mlx-community/QwQ-32B-Preview-8bit'
        # 'mlx-community/QwQ-32B-Preview-bf16'
        # 'mlx-community/Qwen2.5-0.5B-4bit'
        # 'mlx-community/Qwen2.5-32B-Instruct-8bit'
        # 'mlx-community/Qwen2.5-Coder-32B-Instruct-8bit'
        # 'mlx-community/mamba-2.8b-hf-f16'
        # 'mlx-community/Qwen3-30B-A3B-6bit'
    )

    def __init__(self, *configs: Config) -> None:
        super().__init__()

        with tv.consume(*configs) as cc:
            self._model = cc.pop(self.DEFAULT_MODEL)
            self._default_options: tv.TypedValues = DefaultOptions.pop(cc)

    ROLES_MAP: ta.ClassVar[ta.Mapping[type[Message], str]] = {
        SystemMessage: 'system',
        UserMessage: 'user',
        AiMessage: 'assistant',
    }

    def _get_msg_content(self, m: Message) -> str | None:
        if isinstance(m, AiMessage):
            return check.isinstance(m.c, str)

        elif isinstance(m, (SystemMessage, UserMessage)):
            return check.isinstance(m.c, str)

        else:
            raise TypeError(m)

    @lang.cached_function(transient=True)
    def _load_model(self) -> mlxu.LoadedModel:
        # FIXME: walk state, find all mx.arrays, dealloc/set to empty
        check.not_none(self._exit_stack)

        mdl = self._model
        if isinstance(mdl, ModelRepo):
            return mlxu.load_model('/'.join([mdl.namespace, mdl.repo]))
        elif isinstance(mdl, ModelPath):
            return mlxu.load_model(mdl.v)
        else:
            raise TypeError(mdl)

    _OPTION_KWARG_NAMES_MAP: ta.ClassVar[ta.Mapping[str, type[ChatChoicesOptions]]] = dict(
        max_tokens=MaxTokens,
    )

    def invoke(self, request: ChatChoicesRequest) -> ChatChoicesResponse:
        loaded_model = self._load_model()

        tokenizer = loaded_model.tokenization.tokenizer

        if not (
                hasattr(tokenizer, 'apply_chat_template') and
                tokenizer.chat_template is not None
        ):
            raise RuntimeError(tokenizer)

        prompt = tokenizer.apply_chat_template(
            [  # type: ignore[arg-type]
                dict(
                    role=self.ROLES_MAP[type(m)],
                    content=self._get_msg_content(m),
                )
                for m in request.v
            ],
            tokenize=False,
            add_generation_prompt=True,
        )

        kwargs = dict()

        with tv.consume(
                *self._default_options,
                *request.options,
                override=True,
        ) as oc:
            kwargs.update(oc.pop_scalar_kwargs(**self._OPTION_KWARG_NAMES_MAP))

        response = mlxu.generate(
            loaded_model.model,
            loaded_model.tokenization,
            check.isinstance(prompt, str),
            mlxu.GenerationParams(**kwargs),
            # verbose=True,
        )

        return ChatChoicesResponse([
            AiChoice(AiMessage(response))  # noqa
        ])
