"""
TODO:
 - get current revision, package OR live git repo
"""
import contextlib
import dataclasses as dc
import functools
import logging
import signal
import typing as ta

import anyio.abc
import sqlalchemy.ext.asyncio as saa

from omlish import asyncs as au
from omlish import lang
from omlish import logs
from omlish import sql
from omlish.diag import procstats
from omserv.dbs import get_db_url
from omserv.node.registry import NodeRegistrant


ShutdownTrigger: ta.TypeAlias = ta.Callable[..., ta.Awaitable[None]]
ShellApp: ta.TypeAlias = ta.Callable[[ShutdownTrigger], ta.Awaitable[None]]


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


async def killer(shutdown: anyio.Event, sleep_s: float) -> None:
    log.warning('Killing in %d seconds', sleep_s)
    await anyio.sleep(sleep_s)
    log.warning('Killing')
    shutdown.set()


@au.with_adapter_loop(wait=True)
async def a_run_shell(app: ShellApp) -> None:
    async with contextlib.AsyncExitStack() as aes:
        engine = sql.async_adapt(saa.create_async_engine(get_db_url(), echo=True))
        await aes.enter_async_context(lang.a_defer(engine.dispose()))

        nr = NodeRegistrant(
            engine,
            extras={
                'procstats': get_procstats,
            },
        )

        shutdown = anyio.Event()

        async with anyio.create_task_group() as tg:
            await _install_signal_handler(tg, shutdown)

            # tg.start_soon(killer, shutdown, 10.)

            await tg.start(functools.partial(nr.run, shutdown))

            tg.start_soon(functools.partial(app, shutdown.wait))

            log.info('Node running')


def run_shell(app: ShellApp) -> None:
    logs.configure_standard_logging('DEBUG')

    # _backend = 'asyncio'
    _backend = 'trio'

    if _backend == 'trio':
        from omlish.diag.pydevd import patch_for_trio_asyncio  # noqa
        patch_for_trio_asyncio()  # noqa

    anyio.run(functools.partial(a_run_shell, app), backend=_backend)
