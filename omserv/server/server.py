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


class Handler(abc.ABC):
    @abc.abstractmethod
    async def __call__(self, request: aweb.Request) -> aweb.StreamResponse:
        raise NotImplementedError


class HelloHandler(Handler):
    async def __call__(self, request: aweb.Request) -> aweb.StreamResponse:
        return aweb.Response(text="Hello, World!")


# async def _a_main() -> None:
#     app = aweb.Application()
#     app.add_routes([aweb.get('/', HelloHandler())])
#
#     aweb.run_app(app)
#
#     loop = asyncio.get_event_loop()
#     runner = aweb.AppRunner(app)
#     await runner.setup()
#     site = aweb.TCPSite(runner)
#     await site.start()
#     await asyncio.Event().wait()
#
#
# if __name__ == '__main__':
#     asyncio.run(_a_main())


def _main() -> None:
    app = aweb.Application()
    app.add_routes([aweb.get('/', HelloHandler())])

    aweb.run_app(app)


if __name__ == '__main__':
    _main()
