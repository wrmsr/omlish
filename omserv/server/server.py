"""
aiojobs

aiopg
aiomysql

aiobotocore

aiorwlock
"""
import abc
import asyncio  # noqa

import aiohttp.web as aweb

from . import runner


class Handler(abc.ABC):
    @abc.abstractmethod
    async def __call__(self, request: aweb.Request) -> aweb.StreamResponse:
        raise NotImplementedError


class HelloHandler(Handler):
    async def __call__(self, request: aweb.Request) -> aweb.StreamResponse:
        return aweb.Response(text="Hello, World!")


async def _a_main() -> None:
    app = aweb.Application()
    app.add_routes([aweb.get('/', HelloHandler())])

    await runner.a_run_app(app)


def _main() -> None:
    app = aweb.Application()
    app.add_routes([aweb.get('/', HelloHandler())])

    runner.run_app(app)


if __name__ == '__main__':
    asyncio.run(_a_main())
    # _main()
