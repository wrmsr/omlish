import dataclasses as dc
import os
import sys
import typing as ta

from omlish import lang

from ..models import Request
from ..models import Response
from ..prompts import Prompt
from ..prompts import PromptModel_


if ta.TYPE_CHECKING:
    import transformers
else:
    transformers = lang.proxy_import('transformers')


@dc.dataclass(frozen=True)
class TransformersPromptModel(PromptModel_):
    DEFAULT_MODEL: ta.ClassVar[str] = (
        'microsoft/phi-2'
        # 'Qwen/Qwen2-0.5B'
        # 'meta-llama/Meta-Llama-3-8B'
    )

    model: str = dc.field(default_factory=lambda: TransformersPromptModel.DEFAULT_MODEL)
    kwargs: ta.Mapping[str, ta.Any] | None = None

    def generate(self, request: Request[Prompt]) -> Response[str]:
        pipeline = transformers.pipeline(
            'text-generation',
            model=self.model,
            **{
                **dict(
                    device='mps' if sys.platform == 'darwin' else 'cuda',
                    token=os.environ.get('HUGGINGFACE_HUB_TOKEN'),
                ),
                **(self.kwargs or {}),
            },
        )
        output = pipeline(request.v.s)
        return Response(output)
