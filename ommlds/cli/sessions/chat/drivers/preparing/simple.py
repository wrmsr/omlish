from ...... import minichain as mc
from .types import ChatPreparer


##


class SimpleChatPreparer(ChatPreparer):
    async def prepare_chat(self, chat: 'mc.Chat') -> 'mc.Chat':
        return [m for m in chat]  # noqa
