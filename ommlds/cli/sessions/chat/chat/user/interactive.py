import typing as ta

from ...... import minichain as mc
from .....inputs.asyncs import AsyncStringInput
from .....inputs.asyncs import SyncAsyncStringInput
from .....inputs.sync import InputSyncStringInput
from .types import UserChatInput


##


class InteractiveUserChatInput(UserChatInput):
    DEFAULT_STRING_INPUT: ta.ClassVar[AsyncStringInput] = SyncAsyncStringInput(InputSyncStringInput())

    def __init__(
            self,
            string_input: AsyncStringInput | None = None,
    ) -> None:
        super().__init__()

        if string_input is None:
            string_input = self.DEFAULT_STRING_INPUT
        self._string_input = string_input

    async def get_next_user_messages(self) -> 'mc.UserChat':
        try:
            s = await self._string_input()
        except EOFError:
            return []
        return [mc.UserMessage(s)]
