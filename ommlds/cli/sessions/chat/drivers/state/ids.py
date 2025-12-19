from .storage import StateStorage
from .types import ChatId


##


_LAST_CHAT_ID_STATE_KEY: str = 'last_chat_id'


class LastChatIdManager:
    def __init__(
            self,
            *,
            state_storage: StateStorage,
    ) -> None:
        super().__init__()

        self._state_storage = state_storage

    async def get_last_chat_id(self) -> ChatId | None:
        return await self._state_storage.load_state(_LAST_CHAT_ID_STATE_KEY, ChatId)

    async def set_last_chat_id(self, chat_id: ChatId | None) -> None:
        await self._state_storage.save_state(_LAST_CHAT_ID_STATE_KEY, chat_id, ChatId)
