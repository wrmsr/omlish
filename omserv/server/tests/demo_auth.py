import logging

import anyio

from omlish import logs

from ..config import Config
from ..serving import serve
from .hello import hello_app


def _main():
    logs.configure_standard_logging(logging.INFO)

    async def _a_main():
        await serve(
            hello_app,
            Config(),
            handle_shutdown_signals=True,
        )

    anyio.run(_a_main)


if __name__ == '__main__':
    _main()
