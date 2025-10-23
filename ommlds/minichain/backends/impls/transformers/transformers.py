"""
TODO:
 - strong config types
 - https://huggingface.co/blog/aifeifei798/transformers-streaming-output
"""
import sys
import typing as ta

import transformers as tfm

from omlish import check
from omlish import lang
from omlish import typedvalues as tv

from ....chat.choices.services import ChatChoicesRequest
from ....chat.choices.services import ChatChoicesResponse
from ....chat.choices.services import static_check_is_chat_choices_service
from ....chat.choices.types import AiChoice
from ....chat.messages import AiMessage
from ....chat.messages import Message
from ....chat.messages import SystemMessage
from ....chat.messages import ToolUseMessage
from ....chat.messages import ToolUseResultMessage
from ....chat.messages import UserMessage
from ....chat.stream.services import ChatChoicesStreamRequest
from ....chat.stream.services import ChatChoicesStreamResponse
from ....chat.stream.services import static_check_is_chat_choices_stream_service
from ....completion import CompletionRequest
from ....completion import CompletionResponse
from ....completion import static_check_is_completion_service
from ....configs import Config
from ....models.configs import ModelPath
from ...impls.huggingface.configs import HuggingfaceHubToken


##


# @omlish-manifest $.minichain.backends.strings.manifests.BackendStringsManifest(
#     ['ChatChoicesService', 'ChatChoicesStreamService'],
#     'transformers',
# )


##


class TransformersPipelineKwargs(Config, tv.ScalarTypedValue[ta.Mapping[str, ta.Any]]):
    pass


##


# @omlish-manifest $.minichain.registries.manifests.RegistryManifest(
#     name='transformers',
#     aliases=['tfm'],
#     type='CompletionService',
# )
@static_check_is_completion_service
class TransformersCompletionService(lang.ExitStacked):
    DEFAULT_MODEL: ta.ClassVar[str] = (
        'microsoft/phi-2'
        # 'Qwen/Qwen2-0.5B'
        # 'meta-llama/Meta-Llama-3-8B'
    )

    def __init__(self, *configs: Config) -> None:
        super().__init__()

        with tv.consume(*configs) as cc:
            self._model_path = cc.pop(ModelPath(self.DEFAULT_MODEL))
            self._pipeline_kwargs = cc.pop(TransformersPipelineKwargs, [])
            self._huggingface_hub_token = HuggingfaceHubToken.pop_secret(cc, env='HUGGINGFACE_HUB_TOKEN')

    async def invoke(self, request: CompletionRequest) -> CompletionResponse:
        pkw: dict[str, ta.Any] = dict(
            model=self._model_path.v,
            device='mps' if sys.platform == 'darwin' else 'cuda',
        )
        if self._huggingface_hub_token is not None:
            pkw.update(token=self._huggingface_hub_token.reveal())
        for pkw_cfg in self._pipeline_kwargs:
            pkw.update(pkw_cfg.v)

        pipeline = tfm.pipeline(
            'text-generation',
            **pkw,
        )
        output = pipeline(request.v)

        c = check.isinstance(check.single(output)['generated_text'], str)

        return CompletionResponse(c)


##


def build_chat_message(m: Message) -> ta.Mapping[str, ta.Any]:
    if isinstance(m, SystemMessage):
        return dict(
            role='system',
            content=m.c,
        )

    elif isinstance(m, AiMessage):
        return dict(
            role='assistant',
            content=check.isinstance(m.c, str),
        )

    elif isinstance(m, ToolUseMessage):
        return dict(
            role='assistant',
            tool_calls=[dict(
                id=m.tu.id,
                function=dict(
                    arguments=m.tu.args,
                    name=m.tu.name,
                ),
                type='function',
            )],
        )

    elif isinstance(m, UserMessage):
        return dict(
            role='user',
            content=check.isinstance(m.c, str),
        )

    elif isinstance(m, ToolUseResultMessage):
        return dict(
            role='tool',
            tool_call_id=m.tur.id,
            content=check.isinstance(m.tur.c, str),
        )

    else:
        raise TypeError(m)


##


class BaseTransformersChatChoicesService(lang.ExitStacked):
    DEFAULT_MODEL: ta.ClassVar[str] = (
        'meta-llama/Llama-3.2-1B-Instruct'
    )

    def __init__(self, *configs: Config) -> None:
        super().__init__()

        with tv.consume(*configs) as cc:
            self._model_path = cc.pop(ModelPath(self.DEFAULT_MODEL))
            self._pipeline_kwargs = cc.pop(TransformersPipelineKwargs, [])
            self._huggingface_hub_token = HuggingfaceHubToken.pop_secret(cc, env='HUGGINGFACE_HUB_TOKEN')

    @lang.cached_function(transient=True)
    def _load_pipeline(self) -> tfm.Pipeline:
        # FIXME: unload
        check.not_none(self._exit_stack)

        pkw: dict[str, ta.Any] = dict(
            model=self._model_path.v,
            device='mps' if sys.platform == 'darwin' else 'cuda',
        )
        if self._huggingface_hub_token is not None:
            pkw.update(token=self._huggingface_hub_token.reveal())
        for pkw_cfg in self._pipeline_kwargs:
            pkw.update(pkw_cfg.v)

        return tfm.pipeline(
            'text-generation',
            **pkw,
        )


##


# @omlish-manifest $.minichain.registries.manifests.RegistryManifest(
#     name='transformers',
#     aliases=['tfm'],
#     type='ChatChoicesService',
# )
@static_check_is_chat_choices_service
class TransformersChatChoicesService(BaseTransformersChatChoicesService):
    async def invoke(self, request: ChatChoicesRequest) -> ChatChoicesResponse:
        check.empty(request.options)

        pipeline = self._load_pipeline()

        inputs = [
            build_chat_message(m)
            for m in request.v
        ]

        outputs = pipeline(inputs)

        gts = check.single(outputs)['generated_text']
        ugt, agt = gts
        check.state(ugt['role'] == 'user')
        check.state(agt['role'] == 'assistant')

        return ChatChoicesResponse([AiChoice([AiMessage(agt['content'])])])


##


# @omlish-manifest $.minichain.registries.manifests.RegistryManifest(
#     name='transformers',
#     type='ChatChoicesStreamService',
# )
@static_check_is_chat_choices_stream_service
class TransformersChatChoicesStreamService(BaseTransformersChatChoicesService):
    async def invoke(self, request: ChatChoicesStreamRequest) -> ChatChoicesStreamResponse:
        check.empty(request.options)

        pipeline = self._load_pipeline()  # noqa

        inputs = [  # noqa
            build_chat_message(m)
            for m in request.v
        ]

        # async with UseResources.or_new(request.options) as rs:
        #     async def inner(sink: StreamResponseSink[AiChoicesDeltas]) -> ta.Sequence[ChatChoicesOutputs] | None:
        #         last_role: ta.Any = None
        #
        #         for chunk in output:
        #             check.state(chunk['object'] == 'chat.completion.chunk')
        #
        #             choice = check.single(chunk['choices'])
        #
        #             if not (delta := choice.get('delta', {})):
        #                 continue
        #
        #             # FIXME: check role is assistant
        #             if (role := delta.get('role')) != last_role:
        #                 last_role = role
        #
        #             # FIXME: stop reason
        #
        #             if (content := delta.get('content', '')):
        #                 await sink.emit(AiChoicesDeltas([AiChoiceDeltas([ContentAiChoiceDelta(content)])]))
        #
        #         return None
        #
        #     return await new_stream_response(rs, inner)

        raise NotImplementedError
