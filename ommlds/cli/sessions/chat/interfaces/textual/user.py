import asyncio

from ...... import minichain as mc
from ...drivers.user.types import UserChatInput


##


class QueueUserChatInput(UserChatInput):
    def __init__(self) -> None:
        super().__init__()

        self._queue: asyncio.Queue[mc.UserChat] = asyncio.Queue()

    async def push_next_user_messages(self, chat: 'mc.UserChat') -> None:
        await self._queue.put(chat)

    async def get_next_user_messages(self) -> 'mc.UserChat':
        return await self._queue.get()
