from ...drivers.driver import ChatDriver
from ..base import ChatInterface
from .app import ChatApp


##


class TextualChatInterface(ChatInterface):
    def __init__(
            self,
            *,
            driver: ChatDriver,
            app: ChatApp,
    ) -> None:
        super().__init__()

        self._driver = driver
        self._app = app

    async def run(self) -> None:
        await self._app.run_async()
