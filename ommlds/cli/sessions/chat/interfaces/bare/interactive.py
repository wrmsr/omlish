import typing as ta

from .....inputs.asyncs import AsyncStringInput
from .....inputs.asyncs import SyncAsyncStringInput
from .....inputs.sync import InputSyncStringInput
from ...drivers.types import ChatDriver
from ...facades.facade import ChatFacade
from ..base import ChatInterface


##


class InteractiveBareChatInterface(ChatInterface):
    DEFAULT_STRING_INPUT: ta.ClassVar[AsyncStringInput] = SyncAsyncStringInput(InputSyncStringInput())

    def __init__(
            self,
            *,
            driver: ChatDriver,
            facade: ChatFacade,
            string_input: AsyncStringInput | None = None,
    ) -> None:
        super().__init__()

        self._driver = driver
        self._facade = facade
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

            print()
            print('<')
            print()

            await self._facade.handle_user_input(s)

            print()

        await self._driver.stop()
