import datetime
import uuid

from omlish import dataclasses as dc
from omlish import lang
from omlish import orm


##


@dc.dataclass(kw_only=True)
@dc.extra_class_params(install_class_field_attrs='instance')
class DriverState:
    id: orm.Key[uuid.UUID] = dc.field(default_factory=orm.key_wrapping(uuid.uuid4))

    created_at: datetime.datetime = orm.auto_value[datetime.datetime]()
    updated_at: datetime.datetime = orm.auto_value[datetime.datetime]()


@lang.cached_function
def model_registry() -> orm.Registry:
    return orm.registry(
        orm.dataclass_mapper(
            DriverState,
            field_options=dict(
                created_at=[orm.CreatedAt()],
                updated_at=[orm.UpdatedAt()],
            ),
        ),
    )
