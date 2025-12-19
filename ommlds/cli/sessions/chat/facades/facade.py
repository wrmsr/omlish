from ..... import minichain as mc
from ..drivers.driver import ChatDriver


##


class ChatFacade:
    def __init__(
            self,
            *,
            driver: ChatDriver,
    ) -> None:
        super().__init__()

        self._driver = driver

    async def handle_user_input(self, text: str) -> None:
        await self._driver.send_user_messages([mc.UserMessage(text)])
