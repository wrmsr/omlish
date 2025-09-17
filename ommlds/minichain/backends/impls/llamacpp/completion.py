import contextlib
import os.path
import typing as ta

import llama_cpp as lcc

from omlish import typedvalues as tv

from .....backends import llamacpp as lcu
from ....completion import CompletionOption
from ....completion import CompletionRequest
from ....completion import CompletionResponse
from ....completion import static_check_is_completion_service
from ....configs import Config
from ....llms.types import LlmOption
from ....llms.types import MaxTokens
from ....llms.types import Temperature
from ....models.configs import ModelPath


##


# @omlish-manifest $.minichain.registries.manifests.RegistryManifest(
#     name='llamacpp',
#     type='CompletionService',
# )
@static_check_is_completion_service
class LlamacppCompletionService:
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

        with tv.consume(*configs) as cc:
            self._model_path = cc.pop(ModelPath(self.DEFAULT_MODEL_PATH))

    _OPTION_KWARG_NAMES_MAP: ta.ClassVar[ta.Mapping[str, type[CompletionOption | LlmOption]]] = dict(
        max_tokens=MaxTokens,
        temperatur=Temperature,
    )

    async def invoke(self, request: CompletionRequest) -> CompletionResponse:
        kwargs: dict = dict(
            # temperature=0,
            max_tokens=1024,
            # stop=['\n'],
        )

        with tv.TypedValues(*request.options).consume() as oc:
            kwargs.update(oc.pop_scalar_kwargs(**self._OPTION_KWARG_NAMES_MAP))

        lcu.install_logging_hook()

        with contextlib.ExitStack() as es:
            llm = es.enter_context(contextlib.closing(lcc.Llama(
                model_path=self._model_path.v,
                verbose=False,
            )))

            output = llm.create_completion(
                request.v,
                **kwargs,
            )

            return CompletionResponse(ta.cast(ta.Any, output)['choices'][0]['text'])
