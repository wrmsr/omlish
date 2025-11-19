import contextlib
import typing as ta

from omlish import check
from omlish import lang
from omlish import typedvalues as tv

from .....backends import mlx as mlxu
from ....chat.choices.services import ChatChoicesOutputs
from ....chat.choices.services import ChatChoicesRequest
from ....chat.choices.services import ChatChoicesResponse
from ....chat.choices.services import static_check_is_chat_choices_service
from ....chat.choices.stream.services import ChatChoicesStreamRequest
from ....chat.choices.stream.services import ChatChoicesStreamResponse
from ....chat.choices.stream.services import static_check_is_chat_choices_stream_service
from ....chat.choices.stream.types import AiChoiceDeltas
from ....chat.choices.stream.types import AiChoicesDeltas
from ....chat.choices.types import AiChoice
from ....chat.choices.types import ChatChoicesOptions
from ....chat.messages import AiMessage
from ....chat.messages import Message
from ....chat.messages import SystemMessage
from ....chat.messages import UserMessage
from ....chat.stream.types import ContentAiDelta
from ....configs import Config
from ....llms.types import MaxTokens
from ....models.configs import ModelPath
from ....models.configs import ModelRepo
from ....models.configs import ModelSpecifier
from ....resources import UseResources
from ....standard import DefaultOptions
from ....stream.services import StreamResponseSink
from ....stream.services import new_stream_response


##


# @omlish-manifest $.minichain.backends.strings.manifests.BackendStringsManifest(
#     ['ChatChoicesService', 'ChatChoicesStreamService'],
#     'mlx',
# )


##


class BaseMlxChatChoicesService(lang.ExitStacked):
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
        # 'mlx-community/Qwen3-30B-A3B-6bit'
        # 'mlx-community/mamba-2.8b-hf-f16'
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
        if isinstance(m, (AiMessage, SystemMessage, UserMessage)):
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

    @lang.cached_function(transient=True)
    def _get_tokenizer(self) -> mlxu.tokenization.Tokenizer:
        tokenizer = self._load_model().tokenization.tokenizer

        if not (
                hasattr(tokenizer, 'apply_chat_template') and
                tokenizer.chat_template is not None
        ):
            raise RuntimeError(tokenizer)

        return tokenizer

    def _build_prompt(self, messages: ta.Sequence[Message]) -> str:
        return check.isinstance(self._get_tokenizer().apply_chat_template(
            [  # type: ignore[arg-type]
                dict(
                    role=self.ROLES_MAP[type(m)],
                    content=self._get_msg_content(m),
                )
                for m in messages
            ],
            tokenize=False,
            add_generation_prompt=True,
        ), str)

    def _build_kwargs(self, oc: tv.TypedValuesConsumer) -> dict[str, ta.Any]:
        kwargs: dict[str, ta.Any] = {}
        kwargs.update(oc.pop_scalar_kwargs(**self._OPTION_KWARG_NAMES_MAP))
        return kwargs


# @omlish-manifest $.minichain.registries.manifests.RegistryManifest(
#     name='mlx',
#     type='ChatChoicesService',
# )
@static_check_is_chat_choices_service
class MlxChatChoicesService(BaseMlxChatChoicesService):
    async def invoke(self, request: ChatChoicesRequest) -> ChatChoicesResponse:
        loaded_model = self._load_model()

        prompt = self._build_prompt(request.v)

        with tv.consume(
                *self._default_options,
                *request.options,
                override=True,
        ) as oc:
            kwargs = self._build_kwargs(oc)

        response = mlxu.generate(
            loaded_model.model,
            loaded_model.tokenization,
            check.isinstance(prompt, str),
            mlxu.GenerationParams(**kwargs),
            # verbose=True,
        )

        return ChatChoicesResponse([
            AiChoice([AiMessage(response)])  # noqa
        ])


# @omlish-manifest $.minichain.registries.manifests.RegistryManifest(
#     name='mlx',
#     type='ChatChoicesStreamService',
# )
@static_check_is_chat_choices_stream_service
class MlxChatChoicesStreamService(BaseMlxChatChoicesService):
    def __init__(self, *configs: Config) -> None:
        super().__init__()

        with tv.consume(*configs) as cc:
            self._model = cc.pop(MlxChatChoicesService.DEFAULT_MODEL)
            self._default_options: tv.TypedValues = DefaultOptions.pop(cc)

    READ_CHUNK_SIZE = 64 * 1024

    async def invoke(
            self,
            request: ChatChoicesStreamRequest,
            *,
            max_tokens: int = 4096,  # FIXME: ChatOption
    ) -> ChatChoicesStreamResponse:
        loaded_model = self._load_model()

        prompt = self._build_prompt(request.v)

        with tv.consume(
                *self._default_options,
                *request.options,
                override=True,
        ) as oc:
            oc.pop(UseResources, None)
            kwargs = self._build_kwargs(oc)

        async with UseResources.or_new(request.options) as rs:
            gen: ta.Iterator[mlxu.GenerationOutput] = rs.enter_context(contextlib.closing(mlxu.stream_generate(
                loaded_model.model,
                loaded_model.tokenization,
                check.isinstance(prompt, str),
                mlxu.GenerationParams(**kwargs),
                # verbose=True,
            )))

            async def inner(sink: StreamResponseSink[AiChoicesDeltas]) -> ta.Sequence[ChatChoicesOutputs]:
                for go in gen:
                    if go.text:
                        await sink.emit(AiChoicesDeltas([AiChoiceDeltas([
                            ContentAiDelta(go.text),
                        ])]))

                return []

            return await new_stream_response(rs, inner)
