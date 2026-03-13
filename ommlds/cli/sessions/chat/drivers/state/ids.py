from ...... import minichain as mc
from .storage import StateStorage


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

    async def get_last_chat_id(self) -> mc.drivers.ChatId | None:
        return await self._state_storage.load_state(_LAST_CHAT_ID_STATE_KEY, mc.drivers.ChatId)

    async def set_last_chat_id(self, chat_id: mc.drivers.ChatId | None) -> None:
        await self._state_storage.save_state(_LAST_CHAT_ID_STATE_KEY, chat_id, mc.drivers.ChatId)
