import typing as ta

from ..base import Entrypoint
from .interfaces.base import ChatInterface


##


@ta.final
class ChatEntrypoint(Entrypoint):
    def __init__(
            self,
            *,
            interface: ChatInterface,
    ) -> None:
        super().__init__()

        self._interface = interface

    async def run(self) -> None:
        await self._interface.run()
