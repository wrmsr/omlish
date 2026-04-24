from omlish import check

from .... import minichain as mc
from ..base import Mode
from .configs import CompletionConfig


##


class CompletionMode(Mode):
    def __init__(
            self,
            config: CompletionConfig,
            *,
            service_provider: mc.ServiceProvider[mc.CompletionService],
    ) -> None:
        super().__init__()

        self._config = config
        self._service_provider = service_provider

    async def run(self) -> None:
        prompt = check.isinstance(self._config.content, str)

        mdl: mc.CompletionService
        async with self._service_provider.provide_service() as mdl:
            response = await mdl.invoke(mc.CompletionRequest(prompt))

        print(response.v.strip())
