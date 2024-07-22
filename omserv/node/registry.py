import contextlib
import dataclasses as dc
import socket
import uuid

import anyio
import sqlalchemy as sa
import sqlalchemy.ext.asyncio

from omlish import asyncs as au
from omlish import check

from ..secrets import load_secrets  # noqa


meta = sa.MetaData()


_nodes_table = sa.Table(
    '_nodes',
    meta,

    sa.Column('_id', sa.Integer, primary_key=True, autoincrement=True),
    sa.Column('name', sa.String(50), nullable=False, unique=True),

    sa.Index('_node_by_name', 'name', unique=True),
)


@dc.dataclass()
class NodeInfo:
    uuid: str
    hostname: str


@au.mark_anyio
async def register_node(engine: sa.Engine) -> None:
    ni = NodeInfo(
        uuid=str(uuid.uuid4()).replace('-', ''),
        hostname=socket.gethostname(),
    )

    async with contextlib.AsyncExitStack() as aes:
        conn = await au.from_asyncio(aes.enter_async_context)(engine.connect())
        txn = await au.from_asyncio(aes.enter_async_context)(conn.begin())  # noqa

        result = await au.from_asyncio(conn.execute)(sa.select(1))
        print(result.fetchall())


def _get_db_url() -> str:
    cfg = load_secrets()

    host = cfg['postgres_host']
    port = 5432
    user = cfg['postgres_user']
    password = cfg['postgres_pass']

    return f'postgresql+asyncpg://{user}:{password}@{host}:{port}'


async def _a_main() -> None:
    engine = sa.ext.asyncio.create_async_engine(_get_db_url(), echo=True)
    await register_node(engine)


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
