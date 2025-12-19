from omlish import check

from .... import minichain as mc
from ...backends.types import CompletionServiceBackendProvider
from ..base import Session
from .configs import CompletionConfig


##


class CompletionSession(Session):
    def __init__(
            self,
            config: CompletionConfig,
            *,
            service_provider: CompletionServiceBackendProvider,
    ) -> None:
        super().__init__()

        self._config = config
        self._service_provider = service_provider

    async def run(self) -> None:
        prompt = check.isinstance(self._config.content, str)

        mdl: mc.CompletionService
        async with self._service_provider.provide_backend() as mdl:
            response = await mdl.invoke(mc.CompletionRequest(prompt))

        print(response.v.strip())
