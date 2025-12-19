from omlish import check
from omlish import dataclasses as dc
from omlish import lang
from omlish import typedvalues as tv

from ...... import minichain as mc
from .....state.storage import StateStorage
from .types import ChatId
from .types import ChatState
from .types import ChatStateManager


##


class ChatStateStorageKey(tv.UniqueScalarTypedValue[str]):
    pass


def build_chat_storage_key(chat_id: ChatId) -> ChatStateStorageKey:
    return ChatStateStorageKey(f'chat:{chat_id.v}')


##


class StateStorageChatStateManager(ChatStateManager):
    def __init__(
            self,
            *,
            storage: StateStorage,
            key: ChatStateStorageKey,
    ) -> None:
        super().__init__()

        self._storage = storage
        self._key = check.isinstance(key, ChatStateStorageKey)

        self._state: ChatState | None = None

    async def get_state(self) -> ChatState:
        if self._state is not None:
            return self._state
        state: ChatState | None = await self._storage.load_state(self._key.v, ChatState)
        if state is None:
            state = ChatState()
        self._state = state
        return state

    async def extend_chat(self, chat_additions: 'mc.Chat') -> ChatState:
        state = await self.get_state()
        state = dc.replace(
            state,
            chat=[*state.chat, *chat_additions],
            updated_at=lang.utcnow(),
        )
        await self._storage.save_state(self._key.v, state, ChatState)
        self._state = state
        return state
