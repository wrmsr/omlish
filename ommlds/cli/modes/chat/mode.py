import typing as ta

from ..base import Mode
from .interfaces.base import ChatInterface


##


@ta.final
class ChatMode(Mode):
    def __init__(
            self,
            *,
            interface: ChatInterface,
    ) -> None:
        super().__init__()

        self._interface = interface

    async def run(self) -> None:
        await self._interface.run()
