"""
aiojobs

aiopg
aiomysql

aiobotocore

aiorwlock
"""
import abc
import aiohttp.web


class Handler(abc.ABC):
    @abc.abstractmethod
    async def __call__(self, request: aiohttp.web.Request) -> aiohttp.web.StreamResponse:
        raise NotImplementedError


class HelloHandler(Handler):
    async def __call__(self, request: aiohttp.web.Request) -> aiohttp.web.StreamResponse:
        return aiohttp.web.Response(text="Hello, World!")


def _main() -> None:
    app = aiohttp.web.Application()
    app.add_routes([aiohttp.web.get('/', HelloHandler())])

    aiohttp.web.run_app(app)


if __name__ == '__main__':
    _main()
