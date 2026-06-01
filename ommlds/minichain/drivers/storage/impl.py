import typing as ta

from omlish import check
from omlish import orm

from ...chat.messages import Chat
from ...chat.messages import Message
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

    async def _get_chat_sequenced_messages(self) -> ta.Sequence[tuple[int, Message]]:
        async with self._orm.new_session():
            orm_driver = await self._get_orm_driver()

            orm_chat = await orm_driver.chat()

            orm_messages = await orm_chat.messages()

            # FIXME: Do this with an ordered/paged ORM query once the query interface supports order_by/limit.
            return tuple(
                (orm_m.seq, orm_m.message)
                for orm_m in sorted(
                    orm_messages,
                    key=lambda orm_m: orm_m.seq,
                )
            )

    async def get_latest_chat_page(self, limit: int) -> ChatPage:
        return make_chat_page_latest(
            await self._get_chat_sequenced_messages(),
            limit,
        )

    async def get_chat_page_before(self, seq: int, limit: int) -> ChatPage:
        return make_chat_page_before(
            await self._get_chat_sequenced_messages(),
            seq,
            limit,
        )

    async def get_chat_page_after(self, seq: int, limit: int) -> ChatPage:
        return make_chat_page_after(
            await self._get_chat_sequenced_messages(),
            seq,
            limit,
        )

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


##


def _make_chat_page(
        sequenced_messages: ta.Sequence[tuple[int, Message]],
        *,
        start: int,
        stop: int,
) -> ChatPage:
    start = max(start, 0)
    stop = min(stop, len(sequenced_messages))
    check.arg(start <= stop)

    page = sequenced_messages[start:stop]

    before_seq: int | None = None
    after_seq: int | None = None

    if page:
        before_seq = page[0][0]
        after_seq = page[-1][0]

    return ChatPage(
        messages=tuple(message for _, message in page),
        has_before=start > 0,
        has_after=stop < len(sequenced_messages),
        before_seq=before_seq,
        after_seq=after_seq,
    )


def make_chat_page_latest(
        sequenced_messages: ta.Sequence[tuple[int, Message]],
        limit: int,
) -> ChatPage:
    check.arg(limit >= 0)

    stop = len(sequenced_messages)
    start = max(stop - limit, 0)

    return _make_chat_page(
        sequenced_messages,
        start=start,
        stop=stop,
    )


def make_chat_page_before(
        sequenced_messages: ta.Sequence[tuple[int, Message]],
        seq: int,
        limit: int,
) -> ChatPage:
    check.arg(limit >= 0)

    stop = next(
        (i for i, (cur_seq, _) in enumerate(sequenced_messages) if cur_seq >= seq),
        len(sequenced_messages),
    )
    start = max(stop - limit, 0)

    return _make_chat_page(
        sequenced_messages,
        start=start,
        stop=stop,
    )


def make_chat_page_after(
        sequenced_messages: ta.Sequence[tuple[int, Message]],
        seq: int,
        limit: int,
) -> ChatPage:
    check.arg(limit >= 0)

    start = next(
        (i for i, (cur_seq, _) in enumerate(sequenced_messages) if cur_seq > seq),
        len(sequenced_messages),
    )
    stop = min(start + limit, len(sequenced_messages))

    return _make_chat_page(
        sequenced_messages,
        start=start,
        stop=stop,
    )
