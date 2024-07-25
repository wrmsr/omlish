"""
TODO:
 - ping self webserver
 - get current revision, package OR live git repo
"""
import dataclasses as dc
import functools
import logging
import signal
import typing as ta

import anyio.abc
import sqlalchemy.ext.asyncio as saa

from omlish import asyncs as au
from omlish import logs
from omlish import sql
from omlish.diag import procstats

from .. import server
from ..node.dbs import get_db_url
from ..node.models import recreate_all
from ..node.registry import NodeRegistrant
from ..server.tests.hello import hello_app


log = logging.getLogger(__name__)


async def _install_signal_handler(
        tg: anyio.abc.TaskGroup,
        event: anyio.Event | None = None,
        *,
        signals: ta.Iterable[int] = (signal.SIGINT, signal.SIGTERM),
        echo: bool = False,
) -> ta.Callable[..., ta.Awaitable[None]] | None:
    if event is None:
        event = anyio.Event()

    async def _handler(*, task_status=anyio.TASK_STATUS_IGNORED):
        with anyio.open_signal_receiver(*signals) as it:  # type: ignore
            task_status.started()
            async for signum in it:
                if echo:
                    if signum == signal.SIGINT:
                        print('Ctrl+C pressed!')
                    else:
                        print('Terminated!')
                event.set()
                return

    await tg.start(_handler)
    return event.wait


async def get_procstats() -> ta.Mapping[str, ta.Any]:
    return dc.asdict(procstats.get_psutil_procstats())


async def _a_main() -> None:
    engine = sql.async_adapt(saa.create_async_engine(get_db_url(), echo=True))
    await recreate_all(engine)

    nr = NodeRegistrant(
        engine,
        extras={
            'procstats': get_procstats,
        },
    )

    shutdown = anyio.Event()

    async def killer(sleep_s: float) -> None:
        log.warning('Killing in %d seconds', sleep_s)
        await anyio.sleep(sleep_s)
        log.warning('Killing')
        shutdown.set()

    async with anyio.create_task_group() as tg:
        await _install_signal_handler(tg, shutdown)

        # tg.start_soon(killer, 10.)

        await tg.start(functools.partial(nr.run, shutdown))

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
