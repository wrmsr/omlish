import typing as ta

from ...content.content import Content
from ..types import ProvidedSystemMessage
from ..types import SystemMessageProvider


##


class InitialSystemMessageProvider(SystemMessageProvider):
    def __init__(self, content: Content) -> None:
        super().__init__()

        self._content = content

    async def provide_system_messages(self) -> ta.Sequence[ProvidedSystemMessage]:
        return [ProvidedSystemMessage(self._content)]
