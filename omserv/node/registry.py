"""
TODO:
 - async engine / conn adapter :|
 - serverside created_at/updated_at
"""
import contextlib
import dataclasses as dc
import socket
import uuid

import anyio.abc
import sqlalchemy as sa
import sqlalchemy.ext.asyncio as saa

from omlish import asyncs as au
from omlish import check
from omlish import sql

from .dbs import get_db_url
from .models import recreate_all
from .models import Nodes
from .sql import utcnow


##


class GracefulShutdownManager:
    def __init__(self) -> None:
        super().__init__()
        self._shutting_down = False
        self._cancel_scopes: set[anyio.CancelScope] = set()

    def start_shutdown(self) -> None:
        self._shutting_down = True
        for cancel_scope in self._cancel_scopes:
            cancel_scope.cancel()

    def cancel_on_graceful_shutdown(self):
        cancel_scope = anyio.CancelScope()
        self._cancel_scopes.add(cancel_scope)
        if self._shutting_down:
            cancel_scope.cancel()
        return cancel_scope

    @property
    def shutting_down(self) -> bool:
        return self._shutting_down


##


@dc.dataclass()
class NodeInfo:
    uuid: str
    hostname: str


class NodeRegistrant:
    def __init__(
            self,
            engine: sql.AsyncEngineLike,
    ) -> None:
        super().__init__()

        self._engine = sql.async_adapt(engine)

        self._info = NodeInfo(
            uuid=str(uuid.uuid4()).replace('-', ''),
            hostname=socket.gethostname(),
        )

    @au.mark_anyio
    async def __call__(
            self,
            *,
            task_status: anyio.abc.TaskStatus[None] = anyio.TASK_STATUS_IGNORED,
    ) -> None:
        async with contextlib.AsyncExitStack() as aes:
            conn: sql.AsyncConnection = await aes.enter_async_context(self._engine.connect())  # noqa

            async with conn.begin():
                rows = (await conn.execute(
                    sa.select(Nodes).where(Nodes.c.uuid == self._info.uuid)
                )).fetchall()

                nid: int
                if len(rows) > 0:
                    nid = check.single(rows)['_id']

                else:
                    result = await conn.execute(Nodes.insert(), [{
                        'uuid': self._info.uuid,
                        'hostname': self._info.hostname,
                    }])
                    nid = check.single(result.inserted_primary_key)  # noqa

            task_status.started()

            print(f'{nid=}')
            for _ in range(10):
                await anyio.sleep(1.)
                async with conn.begin():  # FIXME: real autocommit lol
                    await conn.execute(sa.update(
                        Nodes
                    ).where(
                        Nodes.c.uuid == self._info.uuid,
                    ).values(
                        heartbeat_at=utcnow(),
                    ))


##


async def _a_main() -> None:
    engine = sql.async_adapt(saa.create_async_engine(get_db_url(), echo=True))
    await recreate_all(engine)

    nr = NodeRegistrant(engine)

    async with anyio.create_task_group() as tg:
        await tg.start(nr)


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
