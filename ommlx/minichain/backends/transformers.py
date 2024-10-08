import os
import sys
import typing as ta

from omlish import lang

from ..prompts import PromptModel
from ..prompts import PromptRequest
from ..prompts import PromptResponse


if ta.TYPE_CHECKING:
    import transformers
else:
    transformers = lang.proxy_import('transformers')


class TransformersPromptModel(PromptModel):
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

    def invoke(self, request: PromptRequest) -> PromptResponse:
        pipeline = transformers.pipeline(
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
        output = pipeline(request.v)
        return PromptResponse(v=output)
