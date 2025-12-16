import typing as ta

from omlish import dataclasses as dc

from ..base import Session
from .configs import ChatConfig
from .interfaces.base import ChatInterface


##


@ta.final
class ChatSession(Session['ChatSession.Config']):
    """
    An adapter to the lower level, dumber, non-chat-specific cli 'session' layer. Nothing else takes the kitchen-sink
    'ChatConfig' object, it's only here for type dispatch in lower layers.
    """

    @dc.dataclass(frozen=True)
    class Config(Session.Config, ChatConfig):
        pass

    def __init__(
            self,
            config: Config,
            *,
            interface: ChatInterface,
    ) -> None:
        super().__init__(config)

        self._interface = interface

    async def run(self) -> None:
        await self._interface.run()
