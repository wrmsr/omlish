"""
TODO:
 - strong config types
"""
import sys
import typing as ta

import transformers as tfm

from omlish import check
from omlish import lang
from omlish import typedvalues as tv

from ...chat.messages import AiMessage
from ...chat.messages import Message
from ...chat.messages import SystemMessage
from ...chat.messages import ToolExecResultMessage
from ...chat.messages import UserMessage
from ...chat.services import ChatRequest
from ...chat.services import ChatResponse
from ...chat.services import ChatService
from ...completion import CompletionRequest
from ...completion import CompletionResponse
from ...completion import CompletionService
from ...configs import Config
from ...configs import consume_configs
from ...standard import ModelPath
from ..huggingface import HuggingfaceHubToken


##


class TransformersPipelineKwargs(Config, tv.ScalarTypedValue[ta.Mapping[str, ta.Any]]):
    pass


##


# @omlish-manifest ommlds.minichain.backends.manifests.BackendManifest(
#     name='transformers',
#     aliases=['tfm'],
#     type='CompletionService',
# )
class TransformersCompletionService(CompletionService, lang.ExitStacked):
    DEFAULT_MODEL: ta.ClassVar[str] = (
        'microsoft/phi-2'
        # 'Qwen/Qwen2-0.5B'
        # 'meta-llama/Meta-Llama-3-8B'
    )

    def __init__(self, *configs: Config) -> None:
        super().__init__()

        with consume_configs(*configs) as cc:
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
        output = pipeline(request.prompt)

        return CompletionResponse(output)


##


def build_chat_message(m: Message) -> ta.Mapping[str, ta.Any]:
    if isinstance(m, SystemMessage):
        return dict(
            role='system',
            content=m.s,
        )

    elif isinstance(m, AiMessage):
        return dict(
            role='assistant',
            content=m.s,
            **(dict(tool_calls=[
                dict(
                    id=te.id,
                    function=dict(
                        arguments=te.args,
                        name=te.spec.name,
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
            content=m.s,
        )

    else:
        raise TypeError(m)


# @omlish-manifest ommlds.minichain.backends.manifests.BackendManifest(
#     name='transformers',
#     aliases=['tfm'],
#     type='ChatService',
# )
class TransformersChatService(ChatService, lang.ExitStacked):
    DEFAULT_MODEL: ta.ClassVar[str] = (
        'meta-llama/Llama-3.2-1B-Instruct'
    )

    def __init__(self, *configs: Config) -> None:
        super().__init__()

        with consume_configs(*configs) as cc:
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

    def invoke(self, request: ChatRequest) -> ChatResponse:
        check.empty(request.options)

        pipeline = self._load_pipeline()

        output = pipeline(
            [
                build_chat_message(m)
                for m in request.chat
            ],
        )

        return ChatResponse(output)
