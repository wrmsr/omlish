from omlish import orm

from ...chat.messages import Chat
from ...chat.metadata import MessageUuid
from ..orm.types import Orm
from ..types import DriverId
from .manager import DriverStorageManager
from .models import OrmChat
from .models import OrmDriver
from .models import OrmMessage
from .types import ChatId
from .types import ChatPage


##


class DriverStorageManagerImpl(DriverStorageManager):
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

    #

    async def _get_orm_chat(self) -> OrmChat:
        if (orm_chat := await orm.get(OrmChat, self._chat_id.v)) is not None:
            return orm_chat

        return await orm.add_one(OrmChat(
            id=orm.key(self._chat_id.v),
        ))

    async def _get_orm_driver(self) -> OrmDriver:
        if (orm_driver := await orm.get(OrmDriver, self._driver_id.v)) is not None:
            return orm_driver

        orm_chat = await self._get_orm_chat()

        return await orm.add_one(OrmDriver(
            id=orm.key(self._driver_id.v),
            chat=orm.ref(orm_chat),
        ))

    async def get_chat(self) -> Chat:
        async with self._orm.new_session():
            orm_driver = await self._get_orm_driver()

            orm_chat = await orm_driver.chat()

            orm_messages = await orm_chat.messages()

            chat = [
                orm_m.message
                for orm_m in sorted(
                    orm_messages,
                    key=lambda orm_m: orm_m.seq,
                )
            ]

        return chat

    #

    @staticmethod
    def _make_chat_page(
            orm_messages: list[OrmMessage],
            *,
            has_before: bool = False,
            has_after: bool = False,
    ) -> ChatPage:
        before_seq: int | None = None
        after_seq: int | None = None

        if orm_messages:
            before_seq = orm_messages[0].seq
            after_seq = orm_messages[-1].seq

        return ChatPage(
            messages=tuple(orm_m.message for orm_m in orm_messages),
            has_before=has_before,
            has_after=has_after,
            before_seq=before_seq,
            after_seq=after_seq,
        )

    async def _get_chat_page_by_seq(
            self,
            *,
            seq_op: orm.WhereOp | orm.WhereOpGlyph,
            seq: int,
            order_by: orm.OrderByDir,
            limit: int,
            reverse: bool = False,
            has_before: bool = False,
            has_after: bool = False,
            overfetch_sets_has_before: bool = False,
            overfetch_sets_has_after: bool = False,
    ) -> ChatPage:
        async with self._orm.new_session():
            orm_driver = await self._get_orm_driver()

            orm_chat = await orm_driver.chat()

            orm_messages = await orm.query(orm.Query(
                OrmMessage,
                orm.Where(
                    orm.WhereItem.of('chat', '=', orm.ref(orm_chat)),
                    orm.WhereItem.of('seq', seq_op, seq),
                ),
                order_by=[
                    orm.OrderByItem('seq', order_by),
                ],
                limit=limit + 1,
            ))

            overfetched = len(orm_messages) > limit
            page_messages = orm_messages[:limit]
            if reverse:
                page_messages = list(reversed(page_messages))

        return self._make_chat_page(
            page_messages,
            has_before=has_before or (overfetched and overfetch_sets_has_before),
            has_after=has_after or (overfetched and overfetch_sets_has_after),
        )

    async def get_latest_chat_page(self, limit: int) -> ChatPage:
        return await self._get_chat_page_by_seq(
            seq_op='>=',
            seq=0,
            order_by='desc',
            limit=limit,
            reverse=True,
            overfetch_sets_has_before=True,
        )

    async def get_chat_page_before(self, seq: int, limit: int) -> ChatPage:
        return await self._get_chat_page_by_seq(
            seq_op='<',
            seq=seq,
            order_by='desc',
            limit=limit,
            reverse=True,
            has_after=True,
            overfetch_sets_has_before=True,
        )

    async def get_chat_page_after(self, seq: int, limit: int) -> ChatPage:
        return await self._get_chat_page_by_seq(
            seq_op='>',
            seq=seq,
            order_by='asc',
            limit=limit,
            has_before=seq > 0,
            overfetch_sets_has_after=True,
        )

    #

    async def extend_chat(self, chat_additions: Chat) -> None:
        async with self._orm.new_session() as sess:  # noqa
            orm_driver = await self._get_orm_driver()

            orm_chat = await orm_driver.chat()

            for m in chat_additions:
                await orm.add_one(OrmMessage(
                    id=orm.key(m.metadata[MessageUuid].v),
                    chat=orm.ref(orm_chat),
                    seq=orm_chat.num_messages + 1,
                    message=m,
                ))

                orm_chat.num_messages += 1
