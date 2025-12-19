import typing as ta

from ..base import Session
from .interfaces.base import ChatInterface


##


@ta.final
class ChatSession(Session):
    def __init__(
            self,
            *,
            interface: ChatInterface,
    ) -> None:
        super().__init__()

        self._interface = interface

    async def run(self) -> None:
        await self._interface.run()
