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
from ....chat.messages import AiMessage
from ....chat.messages import Message
from ....chat.messages import SystemMessage
from ....chat.messages import ToolExecResultMessage
from ....chat.messages import UserMessage
from ....completion import CompletionRequest
from ....completion import CompletionResponse
from ....completion import static_check_is_completion_service
from ....configs import Config
from ....models.configs import ModelPath
from ...impls.huggingface.configs import HuggingfaceHubToken


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

    def invoke(self, request: CompletionRequest) -> CompletionResponse:
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
            **(dict(tool_calls=[
                dict(
                    id=te.id,
                    function=dict(
                        arguments=te.args,
                        name=te.name,
                    ),
                    type='function',
                )
                for te in m.tool_exec_requests
            ]) if m.tool_exec_requests else {}),
        )

    elif isinstance(m, UserMessage):
        return dict(
            role='user',
            content=check.isinstance(m.c, str),
        )

    elif isinstance(m, ToolExecResultMessage):
        return dict(
            role='tool',
            tool_call_id=m.id,
            content=check.isinstance(m.c, str),
        )

    else:
        raise TypeError(m)


# @omlish-manifest $.minichain.registries.manifests.RegistryManifest(
#     name='transformers',
#     aliases=['tfm'],
#     type='ChatChoicesService',
# )
@static_check_is_chat_choices_service
class TransformersChatChoicesService(lang.ExitStacked):
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

    def invoke(self, request: ChatChoicesRequest) -> ChatChoicesResponse:
        check.empty(request.options)

        pipeline = self._load_pipeline()

        output = pipeline(
            [
                build_chat_message(m)
                for m in request.v
            ],
        )

        return ChatChoicesResponse(output)
