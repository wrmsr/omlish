import os
import sys
import typing as ta

from omlish import lang

from ...completion import CompletionRequest
from ...completion import CompletionResponse
from ...completion import CompletionService


if ta.TYPE_CHECKING:
    import transformers as tfm
else:
    tfm = lang.proxy_import('transformers')


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

    def __init__(
            self,
            model: str = DEFAULT_MODEL,
            kwargs: ta.Mapping[str, ta.Any] | None = None,
            *,
            token: str | None = None,
    ) -> None:
        super().__init__()

        self._model = model
        self._kwargs = kwargs
        self._token = token

    def invoke(self, request: CompletionRequest) -> CompletionResponse:
        pipeline = tfm.pipeline(
            'text-generation',
            model=self._model,
            **{
                **dict(
                    device='mps' if sys.platform == 'darwin' else 'cuda',
                    token=self._token or os.environ.get('HUGGINGFACE_HUB_TOKEN'),
                ),
                **(self._kwargs or {}),
            },
        )
        output = pipeline(request.prompt)
        return CompletionResponse(output)
