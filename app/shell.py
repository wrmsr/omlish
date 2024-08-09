"""
TODO:
 - get current revision, package OR live git repo
"""
import contextlib
import dataclasses as dc
import functools
import logging
import typing as ta

import anyio.abc

from omlish import asyncs as au
from omlish import inject as inj
from omlish import lang
from omlish import logs
from omlish.asyncs import anyio as anu
from omlish.diag import procstats
from omserv.node import registry as node_reg


ShellApp = ta.NewType('ShellApp', ta.Callable[[anyio.Event], ta.Awaitable[None]])


log = logging.getLogger(__name__)


@dc.dataclass(frozen=True)
class CompositeShellApp:
    apps: ta.AbstractSet[ShellApp]

    @au.mark_anyio
    async def run(
            self,
            shutdown: anyio.Event,
            *,
            task_status: anyio.abc.TaskStatus[None] = anyio.TASK_STATUS_IGNORED,
    ) -> None:
        async with anyio.create_task_group() as tg:
            for app in self.apps:
                tg.start_soon(app)


async def get_procstats() -> ta.Mapping[str, ta.Any]:
    return dc.asdict(procstats.get_psutil_procstats())


def bind_node_registrant() -> inj.Elemental:
    from .dbs import bind_dbs

    return inj.as_elements(
        inj.private(
            inj.bind(node_reg.NodeRegistrant, singleton=True, expose=True),

            inj.map_binder[str, node_reg.ExtrasProvider]().bind('procstats', get_procstats),

            bind_dbs(),
        ),

        inj.bind(ShellApp, tag=node_reg.NodeRegistrant, to_fn=lang.typed_lambda(nr=node_reg.NodeRegistrant)(lambda nr: nr.run)),  # noqa
        inj.set_binder[ShellApp]().bind(inj.Key(ShellApp, tag=node_reg.NodeRegistrant)),
    )


@au.with_adapter_loop(wait=True)
async def a_run_shell(app: ShellApp) -> None:
    async with contextlib.AsyncExitStack() as aes:
        shutdown = anyio.Event()

        async with anyio.create_task_group() as tg:
            await anu.install_shutdown_signal_handler(tg, shutdown)

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
