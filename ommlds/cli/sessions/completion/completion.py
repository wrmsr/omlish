import dataclasses as dc

from omlish import check
from omlish import lang

from .... import minichain as mc
from ..base import Session


##


DEFAULT_COMPLETION_MODEL_BACKEND = 'openai'


class CompletionSession(Session['CompletionSession.Config']):
    @dc.dataclass(frozen=True)
    class Config(Session.Config):
        content: mc.Content

        _: dc.KW_ONLY

        backend: str | None = None

    def __init__(
            self,
            config: Config,
            *,
            backend_catalog: mc.BackendCatalog,
    ) -> None:
        super().__init__(config)

        self._backend_catalog = backend_catalog

    async def run(self) -> None:
        prompt = check.isinstance(self._config.content, str)

        mdl: mc.CompletionService
        with lang.maybe_managing(self._backend_catalog.get_backend(
                mc.CompletionService,
                self._config.backend or DEFAULT_COMPLETION_MODEL_BACKEND,
        )) as mdl:
            response = mdl.invoke(mc.CompletionRequest(prompt))
            print(response.v.strip())
