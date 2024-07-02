import functools
import logging
import itertools

from omlish import logs
import anyio
import sniffio

from .. import server
from ..server.tests.hello import hello_app


log = logging.getLogger(__name__)


async def _ticker(delay_s: int | float = 3.) -> None:
    for i in itertools.count():
        await anyio.sleep(delay_s)
        log.info(f'tick: {i}')


async def _a_main() -> None:
    logs.configure_standard_logging('INFO')

    async with anyio.create_task_group() as tg:
        tg.start_soon(functools.partial(
            server.serve,
            hello_app,
            server.Config(),
            handle_shutdown_signals=sniffio.current_async_library() != 'trio',
        ))
        tg.start_soon(_ticker)


if __name__ == '__main__':
    anyio.run(_a_main)
