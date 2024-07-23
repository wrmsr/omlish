import contextlib
import dataclasses as dc
import logging
import socket
import typing as ta
import uuid

from omlish import asyncs as au
from omlish import check
from omlish import json
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
    extra: ta.Mapping[str, ta.Any]


ExtrasProvider: ta.TypeAlias = ta.Callable[[], ta.Awaitable[ta.Any]]


class NodeRegistrant:
    def __init__(
            self,
            engine: sql.AsyncEngineLike,
            *,
            extras: ta.Mapping[str, ExtrasProvider] | None = None,
    ) -> None:
        super().__init__()

        self._engine = sql.async_adapt(engine)
        self._extras = extras

        self._info = NodeInfo(
            uuid=str(uuid.uuid4()).replace('-', ''),
            hostname=socket.gethostname(),
            extra={},
        )

    async def _update_info(self) -> None:
        extras: dict[str, ta.Any] = {}
        for k, p in (self._extras or {}).items():
            extras[k] = await p()
        self._info = dc.replace(
            self._info,
            extra=extras,
        )

    @au.mark_anyio
    async def run(
            self,
            shutdown: anyio.Event,
            *,
            task_status: anyio.abc.TaskStatus[None] = anyio.TASK_STATUS_IGNORED,
    ) -> None:
        await self._update_info()

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
                        'extra': json.dumps_compact(self._info.extra),
                    }])
                    nid = check.single(result.inserted_primary_key)  # noqa

                # await conn.execute(sa.select(sa.func.pg_advisory_lock(sa.column('_id'))).select_from(t1))

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

                await self._update_info()

                async with conn.begin():  # FIXME: real autocommit lol
                    await conn.execute(sa.update(
                        Nodes
                    ).where(
                        Nodes.c.uuid == self._info.uuid,
                    ).values(
                        heartbeat_at=utcnow(),
                        extra=json.dumps_compact(self._info.extra),
                    ))
