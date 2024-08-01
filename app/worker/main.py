"""
TODO:
 - ping self webserver
"""
import logging

import anyio.abc

from ..shell import ShutdownTrigger


log = logging.getLogger(__name__)


async def worker_main(shutdown_trigger: ShutdownTrigger) -> None:
    async with anyio.create_task_group() as tg:  # noqa
        log.info('Worker running')

        await shutdown_trigger()
