import contextlib
import dataclasses as dc
import socket
import uuid

import anyio
import sqlalchemy as sa
import sqlalchemy.ext.asyncio as saa

from omlish import asyncs as au

from ..secrets import load_secrets  # noqa


meta = sa.MetaData()


_nodes_table = sa.Table(
    '_nodes',
    meta,

    sa.Column('_id', sa.Integer, primary_key=True, autoincrement=True),
    sa.Column('name', sa.String(50), nullable=False, unique=True),

    sa.Index('_nodes_by_name', 'name', unique=True),
)


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
            txn = await aes.enter_async_context(au.adapt_context(conn.begin()))  # noqa

            result = await au.adapt(conn.execute)(sa.select(1))
            print(result.fetchall())


def _get_db_url() -> str:
    cfg = load_secrets()
    return f'postgresql+asyncpg://{cfg["postgres_user"]}:{cfg["postgres_pass"]}@{cfg["postgres_host"]}:5432'


async def _a_main() -> None:
    engine = saa.create_async_engine(_get_db_url(), echo=True)
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
