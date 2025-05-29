import dataclasses as dc
import typing as ta

from omlish import check
from omlish import lang

from ... import minichain as mc
from .base import Session


if ta.TYPE_CHECKING:
    from ...minichain.backends.llamacpp import completion as mc_lcc_completion
    from ...minichain.backends.openai import completion as mc_openai_completion
    from ...minichain.backends.transformers import transformers as mc_tfm
else:
    mc_lcc_completion = lang.proxy_import('...minichain.backends.llamacpp.completion', __package__)
    mc_openai_completion = lang.proxy_import('...minichain.backends.openai.completion', __package__)
    mc_tfm = lang.proxy_import('...minichain.backends.transformers.transformers', __package__)


##


DEFAULT_COMPLETION_MODEL_BACKEND = 'openai'

COMPLETION_MODEL_BACKENDS: ta.Mapping[str, ta.Callable[[], type[mc.CompletionService]]] = {
    'llamacpp': lambda: mc_lcc_completion.LlamacppCompletionService,
    'openai': lambda: mc_openai_completion.OpenaiCompletionService,
    'transformers': lambda: mc_tfm.TransformersCompletionService,
}


##


class CompletionSession(Session['CompletionSession.Config']):
    @dc.dataclass(frozen=True)
    class Config(Session.Config):
        content: mc.Content

        _: dc.KW_ONLY

        backend: str | None = None

    def __init__(self, config: Config) -> None:
        super().__init__(config)

    def run(self) -> None:
        prompt = check.isinstance(self._config.content, str)
        with lang.maybe_managing(
                COMPLETION_MODEL_BACKENDS[self._config.backend or DEFAULT_COMPLETION_MODEL_BACKEND]()(),
        ) as mdl:
            response = mdl.invoke(mc.CompletionRequest.new(prompt))
            print(response.text.strip())
