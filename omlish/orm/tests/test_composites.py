"""
plan:
 - create table without rowid
 - primary key clustered (`chat_id`, `seq`)
 - unique not null non-pk index on `id`
"""
import datetime
import typing as ta
import uuid

from ... import dataclasses as dc
from ... import lang
from ... import orm


##


@dc.dataclass(kw_only=True)
class _Base(lang.Abstract):
    id: orm.Key[uuid.UUID] = dc.field(default_factory=orm.key_wrapping(uuid.uuid4))

    created_at: datetime.datetime = orm.auto_value[datetime.datetime]()
    updated_at: datetime.datetime = orm.auto_value[datetime.datetime]()


@dc.dataclass(kw_only=True)
@dc.extra_class_params(install_class_field_attrs='instance')
class DriverChat(_Base):
    num_messages: int = 0

    messages: ta.ClassVar[orm.Backref['DriverMessage']] = orm.backref(lambda: DriverMessage.message)  # type: ignore[misc]  # noqa


@dc.dataclass(kw_only=True)
@dc.extra_class_params(install_class_field_attrs='instance')
class DriverMessage(_Base):
    chat: orm.Ref[DriverChat, uuid.UUID]
    seq: int

    message: str


##


def state_mappers() -> ta.Sequence[orm.Mapper]:
    base_field_options: dict[str, ta.Sequence[orm.FieldOption]] = dict(
        created_at=[orm.CreatedAt()],
        updated_at=[orm.UpdatedAt()],
    )

    return [

        orm.dataclass_mapper(
            DriverChat,
            field_options=dict(
                **base_field_options,
            ),
        ),

        orm.dataclass_mapper(
            DriverMessage,
            field_options=dict(
                **base_field_options,
            ),
        ),

    ]
