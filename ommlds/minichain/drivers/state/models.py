import datetime
import uuid

from omlish import dataclasses as dc
from omlish import orm
from omlish import sql

from ...chat.messages import Chat


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


##


def driver_state_mapper() -> orm.Mapper:
    return orm.dataclass_mapper(
        DriverState,
        field_options=dict(
            created_at=[orm.CreatedAt()],
            updated_at=[orm.UpdatedAt()],
            chat=[
                orm.FieldCodec(orm.MarshalCodec()),
                orm.FieldSqlType(sql.td.String()),
            ],
        ),
    )
