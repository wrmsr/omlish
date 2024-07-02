import functools

from omlish import logs
import anyio
import sniffio

from .. import server
from ..server.tests.hello import hello_app


async def _a_main():
    logs.configure_standard_logging('INFO')

    async with anyio.create_task_group() as tg:
        tg.start_soon(functools.partial(
            server.serve,
            hello_app,
            server.Config(),
            handle_shutdown_signals=sniffio.current_async_library() != 'trio',
        ))


if __name__ == '__main__':
    anyio.run(_a_main)
