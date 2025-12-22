from ..... import minichain as mc
from ..drivers.types import ChatDriver
from .commands.manager import CommandsManager


##


class ChatFacade:
    def __init__(
            self,
            *,
            driver: ChatDriver,
            commands: CommandsManager,
    ) -> None:
        super().__init__()

        self._driver = driver
        self._commands = commands

    async def handle_user_input(self, text: str) -> None:
        if text.startswith('/'):
            await self._commands.run_command_text(text[1:])

        else:
            await self._driver.send_user_messages([mc.UserMessage(text)])
