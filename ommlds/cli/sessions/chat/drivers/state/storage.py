from omlish import check
from omlish import dataclasses as dc
from omlish import lang
from omlish import typedvalues as tv

from ...... import minichain as mc
from .....state.storage import StateStorage


##


class DriverStateStorageKey(tv.UniqueScalarTypedValue[str]):
    pass


def build_driver_storage_key(chat_id: mc.drivers.ChatId) -> DriverStateStorageKey:
    return DriverStateStorageKey(f'chat:{chat_id.v}')


##


class StateStorageDriverStateManager(mc.drivers.StateManager):
    def __init__(
            self,
            *,
            storage: StateStorage,
            key: DriverStateStorageKey,
    ) -> None:
        super().__init__()

        self._storage = storage
        self._key = check.isinstance(key, DriverStateStorageKey)

        self._state: mc.drivers.State | None = None

    async def get_state(self) -> mc.drivers.State:
        if self._state is not None:
            return self._state
        state: mc.drivers.State | None = await self._storage.load_state(self._key.v, mc.drivers.State)
        if state is None:
            state = mc.drivers.State()
        self._state = state
        return state

    async def extend_chat(self, chat_additions: mc.Chat) -> mc.drivers.State:
        state = await self.get_state()
        state = dc.replace(
            state,
            chat=[*state.chat, *chat_additions],
            updated_at=lang.utcnow(),
        )
        await self._storage.save_state(self._key.v, state, mc.drivers.State)
        self._state = state
        return state
