from ..... import minichain as mc
from ..drivers.driver import ChatDriver
from .commands.manager import CommandsManager
from .ui import UiMessageDisplayer


##


class ChatFacade:
    def __init__(
            self,
            *,
            driver: ChatDriver,
            ui_message_displayer: UiMessageDisplayer,
            commands: CommandsManager,
    ) -> None:
        super().__init__()

        self._driver = driver
        self._ui_message_displayer = ui_message_displayer
        self._commands = commands

    async def handle_user_input(self, text: str) -> None:
        if text.startswith('/'):
            await self._ui_message_displayer.display_ui_message(f'You said: {text}')

        else:
            await self._driver.send_user_messages([mc.UserMessage(text)])
