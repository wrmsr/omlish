"""
TODO:
 - get current revision, package OR live git repo
"""
import dataclasses as dc
import functools
import logging
import os.path
import typing as ta

import anyio.abc

from omlish import inject as inj
from omlish import lang
from omlish.asyncs import all as au
from omlish.asyncs import anyio as anu
from omlish.diag import procstats
from omlish.formats import dotenv
from omlish.http import asgi
from omlish.logs import all as logs
from omserv import server
from omserv.nodes import registry as nr


ShellTask = ta.NewType('ShellTask', lang.Func1[anyio.Event, ta.Awaitable[None]])


log = logging.getLogger(__name__)


##


async def killer(shutdown: anyio.Event, sleep_s: float) -> None:
    log.warning('Killing in %d seconds', sleep_s)
    await anyio.sleep(sleep_s)
    log.warning('Killing')
    shutdown.set()


##


def bind_node_registrant() -> inj.Elemental:
    async def get_procstats() -> ta.Mapping[str, ta.Any]:
        return dc.asdict(procstats.get_psutil_procstats())  # noqa

    return inj.as_elements(
        inj.private(
            inj.bind(nr.NodeRegistrant, singleton=True, expose=True),

            inj.bind(nr.ExtrasProvider, tag=get_procstats, to_const=get_procstats),
            inj.map_binder[str, nr.ExtrasProvider]().bind('procstats', inj.Key(nr.ExtrasProvider, tag=get_procstats)),  # noqa
        ),

        inj.bind(ShellTask, tag=nr.NodeRegistrant, to_fn=lang.typed_lambda(o=nr.NodeRegistrant)(lambda o: o.run)),
        inj.set_binder[ShellTask]().bind(inj.Key(ShellTask, tag=nr.NodeRegistrant)),
    )


##


class AsgiServerShellTask:
    def __init__(
            self,
            app: asgi.AsgiApp,
            config: server.Config = server.Config(),
    ) -> None:
        super().__init__()
        self._app = app
        self._config = config

    async def run(
            self,
            shutdown: anyio.Event,
            *,
            task_status: anyio.abc.TaskStatus[ta.Sequence[str]] = anyio.TASK_STATUS_IGNORED,
    ) -> None:
        await server.serve(
            self._app,
            self._config,
            shutdown_trigger=shutdown.wait,
        )


def bind_asgi_server(*args: inj.Elemental) -> inj.Elemental:
    return inj.as_elements(
        inj.private(
            *args,

            inj.bind(AsgiServerShellTask, singleton=True, expose=True),
        ),

        inj.bind(server.Config, to_fn=lambda: server.Config(
            bind=os.environ.get('SERVER_BIND', '127.0.0.1:8000').split(','),
        ), singleton=True),

        inj.bind(ShellTask, tag=AsgiServerShellTask, to_fn=lang.typed_lambda(o=AsgiServerShellTask)(lambda o: o.run)),
        inj.set_binder[ShellTask]().bind(inj.Key(ShellTask, tag=AsgiServerShellTask)),
    )


##


@au.with_adapter_loop(wait=True)
async def a_run_shell(*args: inj.Elemental) -> None:
    async with inj.create_async_managed_injector(*args) as i:
        tasks = await au.s_to_a(i.provide)(ta.AbstractSet[ShellTask])

        shutdown = anyio.Event()
        async with anyio.create_task_group() as tg:
            await anu.install_shutdown_signal_handler(tg, shutdown)

            for task in tasks:
                tg.start_soon(functools.partial(task, shutdown))


def run_shell(*args: inj.Elemental) -> None:
    logs.configure_standard_logging('DEBUG')

    if os.path.isfile('.env'):
        with open('.env') as f:
            for eb in dotenv.parse_dotenv_stream(f):
                if eb.key is not None and eb.value is not None:
                    os.environ[eb.key] = eb.value

    # _backend = 'asyncio'
    _backend = 'trio'

    if _backend == 'trio':
        from omlish.diag.pydevd import patch_for_trio_asyncio  # noqa
        patch_for_trio_asyncio()  # noqa

    anyio.run(functools.partial(a_run_shell, *args), backend=_backend)  # noqa
