import os.path
import typing as ta

from omlish import lang

from ..models import Request
from ..models import Response
from ..prompts import Prompt
from ..prompts import PromptModel


if ta.TYPE_CHECKING:
    import llama_cpp
else:
    llama_cpp = lang.proxy_import('llama_cpp')


class LlamacppPromptModel(PromptModel):
    model_path = os.path.join(
        os.path.expanduser('~/.cache/huggingface/hub'),
        'models--QuantFactory--Meta-Llama-3-8B-GGUF',
        'snapshots',
        '1ca85c857dce892b673b988ad0aa83f2cb1bbd19',
        'Meta-Llama-3-8B.Q8_0.gguf',
    )

    def generate(self, t: Request[Prompt]) -> Response[str]:
        llm = llama_cpp.Llama(
            model_path=self.model_path,
        )

        output = llm.create_completion(
            t.v.s,
            max_tokens=1024,
            stop=["\n"],
        )

        return Response(output['choices'][0]['text'])
