import os.path
import typing as ta

from omlish import lang

from ...prompt import PromptRequest
from ...prompt import PromptResponse
from ...prompt import PromptService


if ta.TYPE_CHECKING:
    import llama_cpp

    from .... import llamacpp as lcu

else:
    llama_cpp = lang.proxy_import('llama_cpp')

    lcu = lang.proxy_import('....llamacpp', __package__)


##


# @omlish-manifest ommlx.minichain.backends.manifests.BackendManifest(name='llamacpp', type='PromptService')
class LlamacppPromptService(PromptService):
    # hf.hf_hub_download(
    #   revision='1ca85c857dce892b673b988ad0aa83f2cb1bbd19',
    #   repo_id='QuantFactory/Meta-Llama-3-8B-GGUF',
    #   filename='Meta-Llama-3-8B.Q8_0.gguf',
    # )
    model_path = os.path.join(
        os.path.expanduser('~/.cache/huggingface/hub'),
        'models--QuantFactory--Meta-Llama-3-8B-GGUF',
        'snapshots',
        '1ca85c857dce892b673b988ad0aa83f2cb1bbd19',
        'Meta-Llama-3-8B.Q8_0.gguf',
    )

    def invoke(self, request: PromptRequest) -> PromptResponse:
        lcu.install_logging_hook()

        llm = llama_cpp.Llama(
            model_path=self.model_path,
        )

        output = llm.create_completion(
            request.prompt,
            max_tokens=1024,
            stop=['\n'],
        )

        return PromptResponse(output['choices'][0]['text'])  # type: ignore
