from omlish.formats import json

from .... import minichain as mc
from ...backends.types import EmbeddingServiceBackendProvider
from ..base import Session
from .configs import EmbeddingConfig


##


class EmbeddingSession(Session):
    def __init__(
            self,
            config: EmbeddingConfig,
            *,
            service_provider: EmbeddingServiceBackendProvider,
    ) -> None:
        super().__init__()

        self._config = config
        self._service_provider = service_provider

    async def run(self) -> None:
        mdl: mc.EmbeddingService
        async with self._service_provider.provide_backend() as mdl:
            response = await mdl.invoke(mc.EmbeddingRequest(self._config.content))

        print(json.dumps_compact(list(map(float, response.v))))
