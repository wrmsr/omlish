from omlish import check
from omlish import dataclasses as dc
from omlish import lang
from omlish import typedvalues as tv

from ....chat.messages import Chat
from ..manager import DriverStateManager
from ..types import ChatId
from ..types import DriverState
from .types import StateStorage


##


class DriverStateStorageKey(tv.UniqueScalarTypedValue[str]):
    pass


def build_driver_storage_key(chat_id: ChatId) -> DriverStateStorageKey:
    return DriverStateStorageKey(f'chat:{chat_id.v}')


##


class StateStorageDriverStateManager(DriverStateManager):
    def __init__(
            self,
            *,
            storage: StateStorage,
            key: DriverStateStorageKey,
    ) -> None:
        super().__init__()

        self._storage = storage
        self._key = check.isinstance(key, DriverStateStorageKey)

        self._state: DriverState | None = None

    async def get_driver_state(self) -> DriverState:
        if self._state is not None:
            return self._state
        state: DriverState | None = await self._storage.load_state(self._key.v, DriverState)
        if state is None:
            state = DriverState()
        self._state = state
        return state

    async def extend_chat(self, chat_additions: Chat) -> DriverState:
        state = await self.get_driver_state()
        state = dc.replace(
            state,
            chat=[*state.chat, *chat_additions],
            updated_at=lang.utcnow(),
        )
        await self._storage.save_state(self._key.v, state, DriverState)
        self._state = state
        return state
