"""
TODO:
 - sync ChatUuid / MessageUuid - store metadatas as own rows?
"""
import datetime
import typing as ta
import uuid

from omlish import dataclasses as dc
from omlish import orm
from omlish import sql

from ...chat.messages import Message


##


@dc.dataclass(kw_only=True)
@dc.extra_class_params(install_class_field_attrs='instance')
class OrmChat:
    id: orm.Key[uuid.UUID] = dc.field(default_factory=orm.key_wrapping(uuid.uuid4))

    created_at: datetime.datetime = orm.auto_value[datetime.datetime]()
    updated_at: datetime.datetime = orm.auto_value[datetime.datetime]()

    #

    name: str | None = None

    num_messages: int = 0

    messages: ta.ClassVar[orm.Backref['OrmMessage']] = orm.backref(lambda: OrmMessage.chat)  # type: ignore[misc]


@dc.dataclass(kw_only=True)
@dc.extra_class_params(install_class_field_attrs='instance')
class OrmMessage:
    id: orm.Key[uuid.UUID] = dc.field(default_factory=orm.key_wrapping(uuid.uuid4))

    created_at: datetime.datetime = orm.auto_value[datetime.datetime]()
    updated_at: datetime.datetime = orm.auto_value[datetime.datetime]()

    #

    chat: orm.Ref[OrmChat, uuid.UUID]
    seq: int

    message: Message


@dc.dataclass(kw_only=True)
@dc.extra_class_params(install_class_field_attrs='instance')
class OrmDriver:
    id: orm.Key[uuid.UUID] = dc.field(default_factory=orm.key_wrapping(uuid.uuid4))

    created_at: datetime.datetime = orm.auto_value[datetime.datetime]()
    updated_at: datetime.datetime = orm.auto_value[datetime.datetime]()

    #

    chat: orm.Ref[OrmChat, uuid.UUID]


##


def state_mappers() -> ta.Sequence[orm.Mapper]:
    return [

        orm.dataclass_mapper(
            OrmChat,
            store_name='chats',
            field_options=dict(
                created_at=[orm.CreatedAt()],
                updated_at=[orm.UpdatedAt()],
            ),
            indexes=['name'],
        ),

        orm.dataclass_mapper(
            OrmMessage,
            store_name='messages',
            field_options=dict(
                created_at=[orm.CreatedAt()],
                updated_at=[orm.UpdatedAt()],
                message=[
                    orm.FieldCodec(orm.CompositeCodec(orm.MarshalCodec(), orm.JsonCodec())),
                    orm.FieldSqlType(sql.td.String()),
                ],
            ),
            indexes=[
                orm.index(
                    ['chat', 'seq'],
                    options=[
                        orm.UniqueIndexOption(),
                        orm.SortedIndexOption(),
                        orm.ClusteredIndexOption(),
                    ],
                ),
            ],
        ),

        orm.dataclass_mapper(
            OrmDriver,
            store_name='drivers',
            field_options=dict(
                created_at=[orm.CreatedAt()],
                updated_at=[orm.UpdatedAt()],
            ),
            indexes=['chat'],
        ),

    ]
