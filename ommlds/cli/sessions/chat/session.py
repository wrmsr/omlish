from omlish import dataclasses as dc

from ..base import Session
from .configs import ChatConfig
from .driver import ChatDriver


##


class ChatSession(Session['ChatSession.Config']):
    @dc.dataclass(frozen=True)
    class Config(Session.Config, ChatConfig):
        pass

    def __init__(
            self,
            config: Config,
            *,
            driver: ChatDriver,
    ) -> None:
        super().__init__(config)

        self._driver = driver

    async def run(self) -> None:
        await self._driver.run()
