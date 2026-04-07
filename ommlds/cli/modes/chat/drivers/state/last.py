import uuid

from omlish import dataclasses as dc
from omlish import orm

from ...... import minichain as mc


##


@dc.dataclass(kw_only=True)
@dc.extra_class_params(install_class_field_attrs='instance')
class LastChatId:
    id: orm.Key[int] = dc.field(default_factory=orm.auto_key[int])

    chat_id: uuid.UUID | None = None


def last_chat_id_mapper() -> orm.Mapper:
    return orm.dataclass_mapper(LastChatId)


##


class LastChatIdManager:
    def __init__(
            self,
            *,
            orm_: mc.drivers.Orm,
    ) -> None:
        super().__init__()

        self._orm = orm_

    async def get_last_chat_id(self) -> mc.drivers.ChatId | None:
        async with self._orm.ensure_session():
            if (row := await orm.query_one(LastChatId)) is not None:
                return mc.drivers.ChatId(row.chat_id) if row.chat_id is not None else None
            return None

    async def set_last_chat_id(self, chat_id: mc.drivers.ChatId | None) -> None:
        async with self._orm.ensure_session():
            if (row := await orm.query_one(LastChatId)) is not None:
                row.chat_id = chat_id.v if chat_id is not None else None
            else:
                await orm.add(LastChatId(chat_id=chat_id.v if chat_id is not None else None))
