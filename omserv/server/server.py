"""
aiojobs

aiomysql
aiopg
aiosqlite

aiorwlock
"""
import abc
import asyncio  # noqa

import aiohttp.web as aw

from . import runner


class Handler(abc.ABC):
    @abc.abstractmethod
    async def __call__(self, request: aw.Request) -> aw.StreamResponse:
        raise NotImplementedError


class HelloHandler(Handler):
    async def __call__(self, request: aw.Request) -> aw.StreamResponse:
        return aw.Response(text='Hello, World!')


async def _a_main() -> None:
    app = aw.Application()
    app.add_routes([aw.get('/', HelloHandler())])

    await runner.a_run_app(app)


def _main() -> None:
    app = aw.Application()
    app.add_routes([aw.get('/', HelloHandler())])

    runner.run_app(app)


if __name__ == '__main__':
    asyncio.run(_a_main())
    # _main()
