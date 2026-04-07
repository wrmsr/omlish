from omlish import orm

from ...chat.messages import Chat
from ..orm.types import Orm
from ..types import DriverId
from .manager import DriverStateManager
from .models import DriverChat
from .models import DriverMessage
from .models import DriverState
from .types import ChatId


##


class DriverStateManagerImpl(DriverStateManager):
    def __init__(
            self,
            *,
            driver_id: DriverId,
            chat_id: ChatId,
            orm_: Orm,
    ) -> None:
        super().__init__()

        self._driver_id = driver_id
        self._chat_id = chat_id
        self._orm = orm_

    async def _get_d_chat(self) -> DriverChat:
        if (d_chat := await orm.get(DriverChat, self._chat_id.v)) is not None:
            return d_chat

        return await orm.add_one(DriverChat(
            id=orm.key(self._chat_id.v),
        ))

    async def _get_d_state(self) -> DriverState:
        if (d_state := await orm.get(DriverState, self._driver_id.v)) is not None:
            return d_state

        d_chat = await self._get_d_chat()

        return await orm.add_one(DriverState(
            id=orm.key(self._driver_id.v),
            chat=orm.ref(d_chat),
        ))

    async def get_chat(self) -> Chat:
        async with self._orm.new_session():
            d_state = await self._get_d_state()

            d_chat = await d_state.chat()

            d_messages = await d_chat.messages()

            chat = [
                d_m.message
                for d_m in d_messages
            ]

        return chat

    async def extend_chat(self, chat_additions: Chat) -> None:
        async with self._orm.new_session():
            d_state = await self._get_d_state()

            d_chat = await d_state.chat()

            for m in chat_additions:
                await orm.add_one(DriverMessage(
                    chat=orm.ref(d_chat),
                    seq=d_chat.num_messages + 1,
                    message=m,
                ))

                d_chat.num_messages += 1
