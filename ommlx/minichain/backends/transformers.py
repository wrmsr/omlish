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


class TransformersPromptModel(PromptModel_):
    # model = 'meta-llama/Meta-Llama-3-8B"
    model = 'microsoft/phi-2'

    def generate(self, request: Request[Prompt]) -> Response[str]:
        pipeline = transformers.pipeline(
            'text-generation',
            model=self.model,
            device='mps' if sys.platform == 'darwin' else 'cuda',
            token=os.environ.get('HUGGINGFACE_HUB_TOKEN'),
        )
        output = pipeline(request.v.s)
        return Response(output)
