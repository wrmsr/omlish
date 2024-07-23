import contextlib
import dataclasses as dc
import logging
import socket
import uuid

from omlish import asyncs as au
from omlish import check
from omlish import sql
from omlish.asyncs import anyio as anu
import anyio.abc
import sqlalchemy as sa

from .models import Nodes
from .sql import utcnow


log = logging.getLogger(__name__)


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
            shutdown: anyio.Event,
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
                if rows:
                    nid = check.single(rows)['_id']
                else:
                    result = await conn.execute(Nodes.insert(), [{
                        'uuid': self._info.uuid,
                        'hostname': self._info.hostname,
                    }])
                    nid = check.single(result.inserted_primary_key)  # noqa

            log.info('Node started: nid=%d', nid)
            task_status.started()

            while True:
                await anu.first(
                    lambda: anyio.sleep(1.),
                    shutdown.wait,
                )

                if shutdown.is_set():
                    log.info('Node shutting down')
                    break

                async with conn.begin():  # FIXME: real autocommit lol
                    await conn.execute(sa.update(
                        Nodes
                    ).where(
                        Nodes.c.uuid == self._info.uuid,
                    ).values(
                        heartbeat_at=utcnow(),
                    ))
