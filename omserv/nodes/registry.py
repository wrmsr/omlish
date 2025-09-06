import contextlib
import dataclasses as dc
import socket
import typing as ta
import uuid

import anyio.abc
import sqlalchemy as sa

from omlish import check
from omlish import lang
from omlish.asyncs import all as au
from omlish.asyncs import anyio as anu
from omlish.logs import all as logs
from omlish.sql import alchemy as sau

from .models import Nodes
from .models import setup_db
from .sql import utcnow


log = logs.get_module_logger(globals())


##


@dc.dataclass()
class NodeInfo:
    uuid: str
    hostname: str
    extra: ta.Mapping[str, ta.Any]


ExtrasProvider = ta.NewType('ExtrasProvider', lang.Func0[ta.Awaitable[ta.Any]])


class NodeRegistrant:
    def __init__(
            self,
            engine: sau.AsyncEngine,
            *,
            extras: ta.Mapping[str, ExtrasProvider] | None = None,
    ) -> None:
        super().__init__()

        self._engine = check.isinstance(engine, sau.AsyncEngine)
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
        await setup_db(self._engine)

        await self._update_info()

        async with contextlib.AsyncExitStack() as aes:
            conn: sau.AsyncConnection = await aes.enter_async_context(self._engine.connect())  # noqa

            async with conn.begin():
                rows = (await conn.execute(
                    sa.select(Nodes).where(Nodes.c.uuid == self._info.uuid),
                )).fetchall()

                nid: int
                if rows:
                    nid = check.single(rows)['_id']
                else:
                    result = await conn.execute(Nodes.insert(), [{
                        'uuid': self._info.uuid,
                        'hostname': self._info.hostname,
                        'extra': self._info.extra,
                    }])
                    nid = check.single(result.inserted_primary_key)  # noqa

                # await conn.execute(sa.select(sa.func.pg_advisory_lock(sa.column('_id'))).select_from(t1))

            log.info('Node started: nid=%d', nid)
            task_status.started()

            start_t = end_t = 0.
            while True:
                await anu.first(
                    lambda: anyio.sleep(max(0, 1. - (end_t - start_t))),  # noqa
                    shutdown.wait,
                )
                start_t = anyio.current_time()

                if shutdown.is_set():
                    log.info('Node shutting down')
                    break

                await self._update_info()

                async with conn.begin():  # FIXME: real autocommit lol
                    await conn.execute(sa.update(
                        Nodes,
                    ).where(
                        Nodes.c.uuid == self._info.uuid,
                    ).values(
                        heartbeat_at=utcnow(),
                        extra=self._info.extra,
                    ))

                end_t = anyio.current_time()
