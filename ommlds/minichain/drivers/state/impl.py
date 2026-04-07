from omlish import check
from omlish import orm

from ...chat.messages import Chat
from ..orm.types import Orm
from .manager import DriverStateManager
from .models import DriverState
from .types import ChatId


##


class DriverStateManagerImpl(DriverStateManager):
    def __init__(
            self,
            *,
            chat_id: ChatId,
            orm_: Orm,
    ) -> None:
        super().__init__()

        self._chat_id = chat_id
        self._orm = orm_

    async def get_driver_state(self) -> DriverState:
        async with self._orm.new_session():
            state = await orm.get(DriverState, self._chat_id.v)
            if state is None:
                state = await orm.add_one(DriverState(id=orm.key(self._chat_id.v)))

        return check.not_none(state)

    async def extend_chat(self, chat_additions: Chat) -> DriverState:
        async with self._orm.new_session():
            state = check.not_none(await orm.get(DriverState, self._chat_id.v))

            state.chat = [*state.chat, *chat_additions]

        return state
