import os.path
import typing as ta

from omlish import lang

from ...completion import CompletionRequest
from ...completion import CompletionResponse
from ...completion import CompletionService
from ...configs import Config
from ...configs import consume_configs
from ...standard import ModelPath


if ta.TYPE_CHECKING:
    import llama_cpp

    from ....backends import llamacpp as lcu

else:
    llama_cpp = lang.proxy_import('llama_cpp')

    lcu = lang.proxy_import('....backends.llamacpp', __package__)


##


# @omlish-manifest ommlx.minichain.backends.manifests.BackendManifest(name='llamacpp', type='CompletionService')
class LlamacppCompletionService(CompletionService):
    # hf.hf_hub_download(
    #   revision='1ca85c857dce892b673b988ad0aa83f2cb1bbd19',
    #   repo_id='QuantFactory/Meta-Llama-3-8B-GGUF',
    #   filename='Meta-Llama-3-8B.Q8_0.gguf',
    # )
    DEFAULT_MODEL_PATH: ta.ClassVar[str] = os.path.join(
        os.path.expanduser('~/.cache/huggingface/hub'),
        'models--QuantFactory--Meta-Llama-3-8B-GGUF',
        'snapshots',
        '1ca85c857dce892b673b988ad0aa83f2cb1bbd19',
        'Meta-Llama-3-8B.Q8_0.gguf',
    )

    def __init__(self, *configs: Config) -> None:
        super().__init__()

        with consume_configs(*configs) as cc:
            self._model_path = cc.pop(ModelPath(self.DEFAULT_MODEL_PATH))

    def invoke(self, request: CompletionRequest) -> CompletionResponse:
        lcu.install_logging_hook()

        llm = llama_cpp.Llama(
            model_path=self._model_path.v,
        )

        output = llm.create_completion(
            request.prompt,
            max_tokens=1024,
            stop=['\n'],
        )

        return CompletionResponse(output['choices'][0]['text'])  # type: ignore
