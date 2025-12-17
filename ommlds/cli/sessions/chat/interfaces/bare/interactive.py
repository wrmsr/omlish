import typing as ta

from ...... import minichain as mc
from .....inputs.asyncs import AsyncStringInput
from .....inputs.asyncs import SyncAsyncStringInput
from .....inputs.sync import InputSyncStringInput
from ...drivers.driver import ChatDriver
from ..base import ChatInterface


##


class InteractiveBareChatInterface(ChatInterface):
    DEFAULT_STRING_INPUT: ta.ClassVar[AsyncStringInput] = SyncAsyncStringInput(InputSyncStringInput())

    def __init__(
            self,
            *,
            driver: ChatDriver,
            string_input: AsyncStringInput | None = None,
    ) -> None:
        super().__init__()

        self._driver = driver
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

            await self._driver.send_user_messages([mc.UserMessage(s)])

        await self._driver.stop()
