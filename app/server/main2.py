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
from omlish.http.asgi import AsgiApp
from omserv import server
from omserv.node import registry as nr

from .inject import bind as bind_app


Task = ta.NewType('Task', ta.Callable[[anyio.Event], ta.Awaitable[None]])


log = logging.getLogger(__name__)


##


async def get_procstats() -> ta.Mapping[str, ta.Any]:
    return dc.asdict(procstats.get_psutil_procstats())


def bind_node_registrant() -> inj.Elemental:
    from ..dbs import bind_dbs

    return inj.as_elements(
        inj.private(
            inj.bind(nr.NodeRegistrant, singleton=True, expose=True),

            inj.bind(nr.ExtrasProvider, tag=nr.ExtrasProvider, to_const=get_procstats),
            inj.map_binder[str, nr.ExtrasProvider]().bind('procstats', inj.Key(nr.ExtrasProvider, tag=get_procstats)),  # noqa

            bind_dbs(),
        ),

        inj.bind(Task, tag=nr.NodeRegistrant, to_fn=lang.typed_lambda(o=nr.NodeRegistrant)(lambda o: o.run)),
        inj.set_binder[Task]().bind(inj.Key(Task, tag=nr.NodeRegistrant)),
    )


##


class AsgiServerTask:
    def __init__(self, app: AsgiApp) -> None:
        super().__init__()
        self._app = app

    async def run(
            self,
            shutdown: anyio.Event,
            *,
            task_status: anyio.abc.TaskStatus[ta.Sequence[str]] = anyio.TASK_STATUS_IGNORED,
    ) -> None:
        await server.serve(
            self._app,  # type: ignore
            server.Config(),
            shutdown_trigger=shutdown.wait,
        )


def bind_server() -> inj.Elemental:
    return inj.private(
        bind_app(),

        inj.bind(AsgiServerTask, singleton=True, expose=True),

        inj.bind(Task, tag=AsgiServerTask, to_fn=lang.typed_lambda(o=AsgiServerTask)(lambda o: o.run)),
        inj.set_binder[Task]().bind(inj.Key(Task, tag=AsgiServerTask)),
    )


##


@au.with_adapter_loop(wait=True)
async def _a_main() -> None:
    async with inj.create_async_managed_injector(
            bind_node_registrant(),
            bind_server(),
    ) as i:
        tasks = await au.s_to_a(i.provide)(ta.AbstractSet[Task])

        shutdown = anyio.Event()
        async with anyio.create_task_group() as tg:
            await anu.install_shutdown_signal_handler(tg, shutdown)

            for task in tasks:
                tg.start_soon(functools.partial(task, shutdown))


def _main() -> None:
    logs.configure_standard_logging('DEBUG')

    # _backend = 'asyncio'
    _backend = 'trio'

    if _backend == 'trio':
        from omlish.diag.pydevd import patch_for_trio_asyncio  # noqa
        patch_for_trio_asyncio()  # noqa

    anyio.run(_a_main, backend=_backend)  # noqa


if __name__ == '__main__':
    _main()
