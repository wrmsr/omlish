import typing as ta

from ...... import minichain as mc
from .....interfaces.bare.inputs.asyncs import AsyncStringInput
from .....interfaces.bare.inputs.asyncs import SyncAsyncStringInput
from .....interfaces.bare.inputs.sync import InputSyncStringInput
from ...facades.chat import UserInputSender
from ..base import ChatInterface


##


class InteractiveBareChatInterface(ChatInterface):
    DEFAULT_STRING_INPUT: ta.ClassVar[AsyncStringInput] = SyncAsyncStringInput(InputSyncStringInput())

    def __init__(
            self,
            *,
            driver: 'mc.drivers.Driver',
            user_input_sender: UserInputSender,
            string_input: AsyncStringInput | None = None,
    ) -> None:
        super().__init__()

        self._driver = driver
        self._user_input_sender = user_input_sender
        if string_input is None:
            string_input = self.DEFAULT_STRING_INPUT
        self._string_input = string_input

    async def run(self) -> None:
        await self._driver.start()

        while True:
            try:
                s = await self._string_input()
            except EOFError:
                break

            await self._user_input_sender.send_user_input(s, no_echo=True)

        await self._driver.stop()
