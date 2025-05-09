"""
TODO:
 - strong config types
"""
import sys
import typing as ta

from omlish import lang
from omlish import typedvalues as tv

from ...completion import CompletionRequest
from ...completion import CompletionResponse
from ...completion import CompletionService
from ...configs import Config
from ...configs import consume_configs
from ...standard import ModelPath
from ..huggingface import HuggingfaceHubToken


if ta.TYPE_CHECKING:
    import transformers as tfm
else:
    tfm = lang.proxy_import('transformers')


##


class TransformersPipelineKwargs(Config, tv.ScalarTypedValue[ta.Mapping[str, ta.Any]]):
    pass


##


# @omlish-manifest ommlx.minichain.backends.manifests.BackendManifest(
#     name='transformers',
#     aliases=['tfm'],
#     type='CompletionService',
# )
class TransformersCompletionService(CompletionService):
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
