import aiohttp.web


async def handle(request: aiohttp.web.Request) -> aiohttp.web.Response:
    return aiohttp.web.Response(text="Hello, World!")


def _main() -> None:
    app = aiohttp.web.Application()
    app.add_routes([aiohttp.web.get('/', handle)])

    aiohttp.web.run_app(app)


if __name__ == '__main__':
    _main()
