import typing as ta

from omlish.sql import tabledefs as td

from .sql import CREATE_UPDATED_AT_FUNCTION_STATEMENT
from .sql import IdMixin
from .sql import TimestampsMixin
from .sql import install_updated_at_trigger


##


NODE = td.table_def(
    'nodes',

    td.Column('uuid', td.String()),
    td.Column('hostname', td.String()),

    td.Column('heartbeat_at', td.Datetime()),

    td.Column('extra', td.String()),
)


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

    extra = sa.Column(sapg.JSONB)


Nodes = Node.__table__


install_updated_at_trigger(Metadata, 'nodes')


async def setup_db(engine: sau.AsyncEngineLike, *, drop: bool = False) -> None:
    conn: sau.AsyncConnection
    async with sau.async_adapt(engine).connect() as conn:
        async with conn.begin():
            if drop:
                await conn.run_sync(Metadata.drop_all)
            await conn.execute(sa.text(CREATE_UPDATED_AT_FUNCTION_STATEMENT))
            await conn.run_sync(Metadata.create_all)
