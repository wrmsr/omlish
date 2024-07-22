import contextlib
import dataclasses as dc
import datetime
import socket
import typing as ta
import uuid

import anyio
import sqlalchemy as sa
import sqlalchemy.ext.asyncio as saa
import sqlalchemy.orm

from omlish import asyncs as au
from omlish import check

from ..secrets import load_secrets  # noqa


##


Metadata = sa.MetaData()
Base: ta.Any = sa.orm.declarative_base(metadata=Metadata)


class Node(Base):
    __tablename__ = '_nodes'
    __table_args__ = (
        sa.Index('_nodes_by_uuid', 'uuid', unique=True),
    )

    _id = sa.Column(sa.Integer, nullable=False, primary_key=True, autoincrement=True)

    created_at = sa.Column(sa.TIMESTAMP, default=datetime.datetime.utcnow, nullable=False)  # , server_default=sa.text('0'))  # noqa
    updated_at = sa.Column(sa.TIMESTAMP, default=datetime.datetime.utcnow, nullable=False, onupdate=datetime.datetime.utcnow)  # noqa

    uuid = sa.Column(sa.String(50), nullable=False, unique=True)
    hostname = sa.Column(sa.String(100), nullable=False)


Nodes = Node.__table__


##


@dc.dataclass()
class NodeInfo:
    uuid: str
    hostname: str


class NodeRegistrant:
    def __init__(
            self,
            engine: saa.AsyncEngine,
    ) -> None:
        super().__init__()

        self._engine = engine

        self._info = NodeInfo(
            uuid=str(uuid.uuid4()).replace('-', ''),
            hostname=socket.gethostname(),
        )

    @au.mark_anyio
    async def __call__(self) -> None:
        async with contextlib.AsyncExitStack() as aes:
            conn = await aes.enter_async_context(au.adapt_context(self._engine.connect()))

            nid: int

            async with au.adapt_context(conn.begin()):
                rows = (await au.adapt(conn.execute)(
                    sa.select(Nodes).where(Nodes.c.uuid == self._info.uuid)
                )).fetchall()

                if len(rows) > 0:
                    row = check.single(rows)
                    nid = row['_id']

                else:
                    result = await au.adapt(conn.execute)(Nodes.insert(), [{
                        'uuid': self._info.uuid,
                        'hostname': self._info.hostname,
                    }])
                    nid = check.single(result.inserted_primary_key)  # noqa

            print(f'{nid=}')
            await anyio.sleep(10.)


##


def _get_db_url() -> str:
    cfg = load_secrets()
    return f'postgresql+asyncpg://{cfg["postgres_user"]}:{cfg["postgres_pass"]}@{cfg["postgres_host"]}:5432'


async def _a_main() -> None:
    engine = saa.create_async_engine(_get_db_url(), echo=True)

    async with au.adapt_context(engine.connect()) as conn:
        async with au.adapt_context(conn.begin()):
            await au.adapt(conn.run_sync)(Metadata.drop_all)
            await au.adapt(conn.run_sync)(Metadata.create_all)

    await NodeRegistrant(engine)()


if __name__ == '__main__':
    # _backend = 'asyncio'
    _backend = 'trio'

    match _backend:
        case 'asyncio':
            anyio.run(_a_main, backend='asyncio')

        case 'trio':
            from omlish.testing.pydevd import patch_for_trio_asyncio
            patch_for_trio_asyncio()  # noqa

            anyio.run(au.with_trio_asyncio_loop(_a_main), backend='trio')

        case _:
            raise RuntimeError(f'Unknown backend: {_backend}')
