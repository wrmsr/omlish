import contextlib
import os.path
import typing as ta

from omlish import lang
from omlish import typedvalues as tv

from ...completion import CompletionRequest
from ...completion import CompletionRequestOption
from ...completion import CompletionResponse
from ...completion import CompletionService
from ...configs import Config
from ...configs import consume_configs
from ...llms import LlmRequestOption
from ...llms import MaxTokens
from ...llms import Temperature
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

    _OPTION_KWARG_NAMES_MAP: ta.ClassVar[ta.Mapping[str, type[CompletionRequestOption | LlmRequestOption]]] = dict(
        max_tokens=MaxTokens,
        temperatur=Temperature,
    )

    def invoke(self, request: CompletionRequest) -> CompletionResponse:
        kwargs: dict = dict(
            # temperature=0,
            max_tokens=1024,
            # stop=['\n'],
        )

        with tv.TypedValues(*request.options).consume() as oc:
            kwargs.update(oc.pop_scalar_kwargs(**self._OPTION_KWARG_NAMES_MAP))

        lcu.install_logging_hook()

        with contextlib.ExitStack() as es:
            llm = es.enter_context(contextlib.closing(llama_cpp.Llama(
                model_path=self._model_path.v,
                verbose=False,
            )))

            output = llm.create_completion(
                request.prompt,
                **kwargs,
            )

            return CompletionResponse(output['choices'][0]['text'])  # type: ignore
