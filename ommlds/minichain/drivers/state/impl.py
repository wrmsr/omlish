from omlish import orm

from ...chat.messages import Chat
from ...chat.metadata import MessageUuid
from ..orm.types import Orm
from ..types import DriverId
from .manager import DriverStateManager
from .models import OrmChat
from .models import OrmDriver
from .models import OrmMessage
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

    async def _get_orm_chat(self) -> OrmChat:
        if (orm_chat := await orm.get(OrmChat, self._chat_id.v)) is not None:
            return orm_chat

        return await orm.add_one(OrmChat(
            id=orm.key(self._chat_id.v),
        ))

    async def _get_orm_state(self) -> OrmDriver:
        if (orm_driver := await orm.get(OrmDriver, self._driver_id.v)) is not None:
            return orm_driver

        orm_chat = await self._get_orm_chat()

        return await orm.add_one(OrmDriver(
            id=orm.key(self._driver_id.v),
            chat=orm.ref(orm_chat),
        ))

    async def get_chat(self) -> Chat:
        async with self._orm.new_session():
            orm_state = await self._get_orm_state()

            orm_chat = await orm_state.chat()

            orm_messages = await orm_chat.messages()

            chat = [
                orm_m.message
                for orm_m in sorted(
                    orm_messages,
                    key=lambda orm_m: orm_m.seq,
                )
            ]

        return chat

    async def extend_chat(self, chat_additions: Chat) -> None:
        async with self._orm.new_session():
            orm_state = await self._get_orm_state()

            orm_chat = await orm_state.chat()

            for m in chat_additions:
                await orm.add_one(OrmMessage(
                    id=orm.key(m.metadata[MessageUuid].v),
                    chat=orm.ref(orm_chat),
                    seq=orm_chat.num_messages + 1,
                    message=m,
                ))

                orm_chat.num_messages += 1
