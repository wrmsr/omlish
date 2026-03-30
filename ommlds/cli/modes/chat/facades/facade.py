import uuid

from ..... import minichain as mc
from .commands.manager import CommandsManager


##


class ChatFacade:
    def __init__(
            self,
            *,
            driver: 'mc.drivers.Driver',
            commands: CommandsManager,
    ) -> None:
        super().__init__()

        self._driver = driver
        self._commands = commands

    async def handle_user_input(
            self,
            text: str,
            *,
            input_uuid: uuid.UUID | None = None,
    ) -> None:
        if input_uuid is None:
            input_uuid = uuid.uuid4()

        if text.startswith('/'):
            await self._commands.run_command_text(text[1:])

        else:
            msg = mc.UserMessage(text).with_metadata(mc.MessageUuid(input_uuid))

            await self._driver.do_action(mc.drivers.SendUserMessagesAction(
                [msg],
                uuid=input_uuid,
            ))
