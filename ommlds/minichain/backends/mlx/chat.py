import typing as ta

from omlish import check
from omlish import lang
from omlish import typedvalues as tv

from ....backends import mlx as mlxu
from ...chat.choices import AiChoice
from ...chat.messages import AiMessage
from ...chat.messages import Message
from ...chat.messages import SystemMessage
from ...chat.messages import UserMessage
from ...chat.services import ChatRequest
from ...chat.services import ChatResponse
from ...chat.services import ChatService
from ...chat.types import ChatRequestOption
from ...configs import Config
from ...configs import consume_configs
from ...llms.services import LlmRequestOption
from ...llms.services import MaxTokens
from ...standard import DefaultRequestOptions
from ...standard import ModelName


##


# @omlish-manifest ommlds.minichain.backends.manifests.BackendManifest(name='mlx', type='ChatService')
class MlxChatService(ChatService, lang.ExitStacked):
    DEFAULT_MODEL_NAME: ta.ClassVar[str] = (
        # 'mlx-community/DeepSeek-Coder-V2-Lite-Instruct-8bit'
        # 'mlx-community/Llama-3.3-70B-Instruct-4bit'
        # 'mlx-community/Llama-3.3-70B-Instruct-6bit'
        'mlx-community/Llama-3.3-70B-Instruct-8bit'
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

        with consume_configs(*configs) as cc:
            self._model_name = cc.pop(ModelName(self.DEFAULT_MODEL_NAME))
            self._default_options: tv.TypedValues = DefaultRequestOptions.pop(cc)

    ROLES_MAP: ta.ClassVar[ta.Mapping[type[Message], str]] = {
        SystemMessage: 'system',
        UserMessage: 'user',
        AiMessage: 'assistant',
    }

    def _get_msg_content(self, m: Message) -> str | None:
        if isinstance(m, (SystemMessage, AiMessage)):
            return m.s

        elif isinstance(m, UserMessage):
            return check.isinstance(m.c, str)

        else:
            raise TypeError(m)

    @lang.cached_function(transient=True)
    def _load_model(self) -> mlxu.LoadedModel:
        # FIXME: walk state, find all mx.arrays, dealloc/set to empty
        check.not_none(self._exit_stack)

        return mlxu.load_model(self._model_name.v)

    _OPTION_KWARG_NAMES_MAP: ta.ClassVar[ta.Mapping[str, type[ChatRequestOption | LlmRequestOption]]] = dict(
        max_tokens=MaxTokens,
    )

    def invoke(self, request: ChatRequest) -> ChatResponse:
        loaded_model = self._load_model()

        tokenizer = loaded_model.tokenization.tokenizer

        if not (
                hasattr(tokenizer, 'apply_chat_template') and
                tokenizer.chat_template is not None
        ):
            raise RuntimeError(tokenizer)

        prompt = tokenizer.apply_chat_template(
            [
                dict(
                    role=self.ROLES_MAP[type(m)],
                    content=self._get_msg_content(m),
                )
                for m in request.chat
            ],
            tokenize=False,
            add_generation_prompt=True,
        )

        kwargs = dict()

        with tv.TypedValues(
                *self._default_options,
                *request.options,
                override=True,
        ).consume() as oc:
            kwargs.update(oc.pop_scalar_kwargs(**self._OPTION_KWARG_NAMES_MAP))

        response = mlxu.generate(
            loaded_model.model,
            loaded_model.tokenization,
            prompt,
            mlxu.GenerationParams(**kwargs),
            # verbose=True,
        )

        return ChatResponse([
            AiChoice(AiMessage(response))  # noqa
        ])
