import dataclasses as dc
import typing as ta

from omlish import check
from omlish import lang

from ... import minichain as mc
from ...minichain.backends.llamacpp.completion import LlamacppCompletionService
from ...minichain.backends.openai.completion import OpenaiCompletionService
from ...minichain.backends.transformers.transformers import TransformersCompletionService
from .base import Session


##


DEFAULT_COMPLETION_MODEL_BACKEND = 'openai'

COMPLETION_MODEL_BACKENDS: ta.Mapping[str, type[mc.CompletionService]] = {
    'llamacpp': LlamacppCompletionService,
    'openai': OpenaiCompletionService,
    'transformers': TransformersCompletionService,
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
                COMPLETION_MODEL_BACKENDS[self._config.backend or DEFAULT_COMPLETION_MODEL_BACKEND](),
        ) as mdl:
            response = mdl.invoke(mc.CompletionRequest.new(prompt))
            print(response.text.strip())
