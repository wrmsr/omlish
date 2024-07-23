import functools
import logging

from omlish import asyncs as au
from omlish import logs
from omlish import sql
import anyio.abc
import sqlalchemy.ext.asyncio as saa

from .. import server
from ..node.dbs import get_db_url
from ..node.models import recreate_all
from ..node.registry import NodeRegistrant
from ..server.tests.hello import hello_app


log = logging.getLogger(__name__)


async def _a_main() -> None:
    engine = sql.async_adapt(saa.create_async_engine(get_db_url(), echo=True))
    await recreate_all(engine)

    nr = NodeRegistrant(engine)

    shutdown = anyio.Event()

    async def killer(sleep_s: float) -> None:
        log.warning('Killing in %d seconds', sleep_s)
        await anyio.sleep(sleep_s)
        log.warning('Killing')
        shutdown.set()

    async with anyio.create_task_group() as tg:
        # tg.start_soon(killer, 10.)

        await tg.start(functools.partial(nr, shutdown))

        tg.start_soon(functools.partial(
            server.serve,
            hello_app,
            server.Config(),
            shutdown_trigger=shutdown.wait,
        ))

        log.info('Node running')


if __name__ == '__main__':
    logs.configure_standard_logging('DEBUG')

    # _backend = 'asyncio'
    _backend = 'trio'

    match _backend:
        case 'asyncio':
            anyio.run(_a_main, backend='asyncio')

        case 'trio':
            from omlish.testing.pydevd import patch_for_trio_asyncio
            patch_for_trio_asyncio()  # noqa

            anyio.run(au.with_trio_asyncio_loop(_a_main, wait=True), backend='trio')

        case _:
            raise RuntimeError(f'Unknown backend: {_backend}')
