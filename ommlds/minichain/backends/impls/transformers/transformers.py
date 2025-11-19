"""
TODO:
 - strong config types
 - https://huggingface.co/blog/aifeifei798/transformers-streaming-output
"""
import sys
import threading
import typing as ta

import transformers as tfm

from omlish import check
from omlish import lang
from omlish import typedvalues as tv
from omlish.asyncs.asyncio.sync import AsyncioBufferRelay

from .....backends.transformers.filecache import file_cache_patch_context
from .....backends.transformers.streamers import CancellableTextStreamer
from ....chat.choices.services import ChatChoicesRequest
from ....chat.choices.services import ChatChoicesResponse
from ....chat.choices.services import static_check_is_chat_choices_service
from ....chat.choices.stream.services import ChatChoicesStreamRequest
from ....chat.choices.stream.services import ChatChoicesStreamResponse
from ....chat.choices.stream.services import static_check_is_chat_choices_stream_service
from ....chat.choices.stream.types import AiChoiceDeltas  # noqa
from ....chat.choices.stream.types import AiChoicesDeltas  # noqa
from ....chat.choices.types import AiChoice
from ....chat.choices.types import ChatChoicesOutputs
from ....chat.messages import AiMessage
from ....chat.messages import Message
from ....chat.messages import SystemMessage
from ....chat.messages import ToolUseMessage
from ....chat.messages import ToolUseResultMessage
from ....chat.messages import UserMessage
from ....chat.stream.types import ContentAiDelta  # noqa
from ....completion import CompletionRequest
from ....completion import CompletionResponse
from ....completion import static_check_is_completion_service
from ....configs import Config
from ....models.configs import ModelPath
from ....resources import UseResources
from ....stream.services import StreamResponseSink
from ....stream.services import new_stream_response
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

        with file_cache_patch_context(
                local_first=True,
                local_config_present_is_authoritative=True,
        ):
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

        relay: AsyncioBufferRelay = AsyncioBufferRelay()

        def streamer_callback(text: str, *, stream_end: bool) -> None:
            if text or stream_end:
                relay.push(text, *([None] if stream_end else []))

        streamer = CancellableTextStreamer(
            check.not_none(pipeline.tokenizer),  # type: ignore[arg-type]
            streamer_callback,  # noqa
            skip_prompt=True,
            skip_special_tokens=True,
        )

        async with UseResources.or_new(request.options) as rs:
            thread = threading.Thread(
                target=CancellableTextStreamer.ignoring_cancelled(pipeline),
                args=(
                    inputs,
                ),
                kwargs=dict(
                    streamer=streamer,
                ),
            )

            def stop_thread() -> None:
                streamer.cancel()
                # thread.join()

            rs.enter_context(lang.defer(stop_thread))

            thread.start()

            async def inner(sink: StreamResponseSink[AiChoicesDeltas]) -> ta.Sequence[ChatChoicesOutputs] | None:
                while True:
                    await relay.wait()
                    got = relay.swap()

                    if not got:
                        raise RuntimeError

                    if got[-1] is None:
                        out = ''.join(got[:-1])
                        end = True
                    else:
                        out = ''.join(got)
                        end = False

                    if out:
                        await sink.emit(AiChoicesDeltas([AiChoiceDeltas([ContentAiDelta(out)])]))

                    if end:
                        break

                return []

            return await new_stream_response(rs, inner)
