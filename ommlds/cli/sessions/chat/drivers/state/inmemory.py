from omlish import dataclasses as dc
from omlish import lang

from ...... import minichain as mc
from .types import ChatState
from .types import ChatStateManager


##


class InMemoryChatStateManager(ChatStateManager):
    def __init__(self, initial_state: ChatState | None = None) -> None:
        super().__init__()

        if initial_state is None:
            initial_state = ChatState()
        self._state = initial_state

    async def get_state(self) -> ChatState:
        return self._state

    async def clear_state(self) -> ChatState:
        self._state = ChatState()
        return self._state

    async def extend_chat(self, chat_additions: 'mc.Chat') -> ChatState:
        self._state = dc.replace(
            self._state,
            chat=[*self._state.chat, *chat_additions],
            updated_at=lang.utcnow(),
        )
        return self._state
