import typing as ta

from omlish import sql
import sqlalchemy as sa
import sqlalchemy.orm

from .sql import CREATE_UPDATED_AT_FUNCTION_STATEMENT
from .sql import IdMixin
from .sql import TimestampsMixin
from .sql import install_updated_at_trigger


##


Metadata = sa.MetaData()
Base: ta.Any = sa.orm.declarative_base(metadata=Metadata)


class Node(
    IdMixin,
    TimestampsMixin,
    Base,
):
    __tablename__ = 'nodes'
    __table_args__ = (
        sa.Index('nodes_by_uuid', 'uuid', unique=True),
    )

    uuid = sa.Column(sa.String(50), nullable=False, unique=True)
    hostname = sa.Column(sa.String(100), nullable=False)

    heartbeat_at = sa.Column(sa.TIMESTAMP(timezone=True))


Nodes = Node.__table__


install_updated_at_trigger(Metadata, 'nodes')


async def recreate_all(engine: sql.AsyncEngineLike) -> None:
    conn: sql.AsyncConnection
    async with sql.async_adapt(engine).connect() as conn:
        async with conn.begin():
            await conn.run_sync(Metadata.drop_all)
            await conn.execute(sa.text(CREATE_UPDATED_AT_FUNCTION_STATEMENT))
            await conn.run_sync(Metadata.create_all)
