import datetime
import typing as ta
import uuid

from omlish import dataclasses as dc
from omlish import orm
from omlish import sql

from ...chat.messages import Chat
from ...chat.messages import Message


##


@dc.dataclass(kw_only=True)
@dc.extra_class_params(install_class_field_attrs='instance')
class DriverState:
    id: orm.Key[uuid.UUID] = dc.field(default_factory=orm.key_wrapping(uuid.uuid4))

    created_at: datetime.datetime = orm.auto_value[datetime.datetime]()
    updated_at: datetime.datetime = orm.auto_value[datetime.datetime]()

    #

    name: str | None = None

    chat: Chat = ()


@dc.dataclass(kw_only=True)
@dc.extra_class_params(install_class_field_attrs='instance')
class DriverChat:
    id: orm.Key[uuid.UUID] = dc.field(default_factory=orm.key_wrapping(uuid.uuid4))

    created_at: datetime.datetime = orm.auto_value[datetime.datetime]()
    updated_at: datetime.datetime = orm.auto_value[datetime.datetime]()

    #

    name: str | None = None

    num_messages: int = 0

    messages: ta.ClassVar[orm.Backref['DriverMessage']] = orm.backref(lambda: DriverMessage.chat)  # type: ignore[misc]


@dc.dataclass(kw_only=True)
@dc.extra_class_params(install_class_field_attrs='instance')
class DriverMessage:
    id: orm.Key[uuid.UUID] = dc.field(default_factory=orm.key_wrapping(uuid.uuid4))

    created_at: datetime.datetime = orm.auto_value[datetime.datetime]()
    updated_at: datetime.datetime = orm.auto_value[datetime.datetime]()

    #

    chat: orm.Ref[DriverChat, uuid.UUID]
    seq: int

    message: Message


##


def state_mappers() -> ta.Sequence[orm.Mapper]:
    return [
        orm.dataclass_mapper(
            DriverState,
            field_options=dict(
                created_at=[orm.CreatedAt()],
                updated_at=[orm.UpdatedAt()],
                chat=[
                    orm.FieldCodec(orm.CompositeCodec(orm.MarshalCodec(), orm.JsonCodec())),
                    orm.FieldSqlType(sql.td.String()),
                ],
            ),
        ),
    ]
