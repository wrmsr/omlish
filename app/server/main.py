"""
TODO:
 - ping self webserver
"""
import functools
import logging

import anyio.abc

from omserv import server

from ..shell import ShutdownTrigger
from .app import server_app_context


log = logging.getLogger(__name__)


async def server_main(shutdown_trigger: ShutdownTrigger) -> None:
    async with anyio.create_task_group() as tg:
        async with server_app_context() as server_app:
            tg.start_soon(functools.partial(
                server.serve,
                server_app,  # type: ignore
                server.Config(),
                shutdown_trigger=shutdown_trigger,
            ))

            log.info('Server running')
