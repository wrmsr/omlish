from ...drivers.types import ChatDriver
from ..base import ChatInterface


##


class OneshotBareChatInterface(ChatInterface):
    def __init__(
            self,
            *,
            driver: ChatDriver,
    ) -> None:
        super().__init__()

        self._driver = driver

    async def run(self) -> None:
        await self._driver.start()

        await self._driver.stop()
