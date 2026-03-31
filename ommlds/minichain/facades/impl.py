import uuid

from ..chat.messages import UserMessage
from ..chat.metadata import MessageUuid
from ..drivers.actions import SendUserMessagesAction
from ..drivers.types import Driver
from .commands.manager import CommandsManager
from .types import Facade


##


class FacadeImpl(Facade):
    def __init__(
            self,
            *,
            driver: Driver,
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
            msg = UserMessage(text).with_metadata(MessageUuid(input_uuid))

            await self._driver.do_action(SendUserMessagesAction(
                [msg],
                uuid=input_uuid,
            ))
