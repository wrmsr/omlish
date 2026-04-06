from omlish import dataclasses as dc
from omlish import lang

from ...chat.messages import Chat
from .manager import DriverStateManager
from .types import DriverState


##


class InMemoryDriverStateManager(DriverStateManager):
    def __init__(self, initial_state: DriverState | None = None) -> None:
        super().__init__()

        if initial_state is None:
            initial_state = DriverState()
        self._state = initial_state

    async def get_driver_state(self) -> DriverState:
        return self._state

    async def extend_chat(self, chat_additions: Chat) -> DriverState:
        self._state = dc.replace(
            self._state,
            chat=[*self._state.chat, *chat_additions],
            updated_at=lang.utcnow(),
        )
        return self._state
