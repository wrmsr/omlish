from omlish import dataclasses as dc
from omlish import lang

from ...chat.messages import Chat
from .types import State
from .types import StateManager


##


class InMemoryStateManager(StateManager):
    def __init__(self, initial_state: State | None = None) -> None:
        super().__init__()

        if initial_state is None:
            initial_state = State()
        self._state = initial_state

    async def get_state(self) -> State:
        return self._state

    async def extend_chat(self, chat_additions: Chat) -> State:
        self._state = dc.replace(
            self._state,
            chat=[*self._state.chat, *chat_additions],
            updated_at=lang.utcnow(),
        )
        return self._state
