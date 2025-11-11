from omlish import check
from omlish import dataclasses as dc

from .... import minichain as mc
from ...backends.types import CompletionServiceBackendProvider
from ..base import Session
from .configs import CompletionConfig


##


class CompletionSession(Session['CompletionSession.Config']):
    @dc.dataclass(frozen=True)
    class Config(Session.Config, CompletionConfig):
        pass

    def __init__(
            self,
            config: Config,
            *,
            service_provider: CompletionServiceBackendProvider,
    ) -> None:
        super().__init__(config)

        self._service_provider = service_provider

    async def run(self) -> None:
        prompt = check.isinstance(self._config.content, str)

        mdl: mc.CompletionService
        async with self._service_provider.provide_backend() as mdl:
            response = await mdl.invoke(mc.CompletionRequest(prompt))

        print(response.v.strip())
