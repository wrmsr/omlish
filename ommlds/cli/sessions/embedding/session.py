from omlish import dataclasses as dc
from omlish.formats import json

from .... import minichain as mc
from ...backends.types import EmbeddingServiceBackendProvider
from ..base import Session
from .configs import EmbeddingConfig


##


class EmbeddingSession(Session['EmbeddingSession.Config']):
    @dc.dataclass(frozen=True)
    class Config(Session.Config, EmbeddingConfig):
        pass

    def __init__(
            self,
            config: Config,
            *,
            service_provider: EmbeddingServiceBackendProvider,
    ) -> None:
        super().__init__(config)

        self._service_provider = service_provider

    async def run(self) -> None:
        mdl: mc.EmbeddingService
        async with self._service_provider.provide_backend() as mdl:
            response = await mdl.invoke(mc.EmbeddingRequest(self._config.content))

        print(json.dumps_compact(list(map(float, response.v))))
