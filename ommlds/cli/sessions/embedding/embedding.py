import dataclasses as dc

from omlish import lang
from omlish.formats import json

from .... import minichain as mc
from ..base import Session


##


DEFAULT_EMBEDDING_MODEL_BACKEND = 'openai'


class EmbeddingSession(Session['EmbeddingSession.Config']):
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
        mdl: mc.EmbeddingService
        with lang.maybe_managing(self._backend_catalog.get_backend(
            mc.EmbeddingService,
            self._config.backend or DEFAULT_EMBEDDING_MODEL_BACKEND,
        )) as mdl:
            response = mdl.invoke(mc.EmbeddingRequest(self._config.content))
            print(json.dumps_compact(list(map(float, response.v))))
