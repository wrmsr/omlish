import asyncio

from aiohttp.web import run_app
from aiohttp.web_app import Application
from aiohttp.web_request import Request
from aiohttp.web_routedef import get
from aiohttp.web_ws import WebSocketResponse
from textual.constants import DEVTOOLS_PORT

from .service import DevtoolsService


##


DEFAULT_SIZE_CHANGE_POLL_DELAY_SECONDS = 2


async def websocket_handler(request: Request) -> WebSocketResponse:
    """
    aiohttp websocket handler for sending data between devtools client and server

    Args:
        request: The request to the websocket endpoint

    Returns:
        The websocket response
    """

    service: DevtoolsService = request.app['service']
    return await service.handle(request)


async def _on_shutdown(app: Application) -> None:
    """aiohttp shutdown handler, called when the aiohttp server is stopped"""

    service: DevtoolsService = app['service']
    await service.shutdown()


async def _on_startup(app: Application) -> None:
    service: DevtoolsService = app['service']
    await service.start()


def _run_devtools(
        *,
        verbose: bool = False,
        exclude: list[str] | None = None,
        port: int | None = None,
) -> None:
    app = _make_devtools_aiohttp_app(
        port=port,
        verbose=verbose,
        exclude=exclude,
    )

    def noop_print(_: str) -> None:
        pass

    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()

    try:
        run_app(
            app,
            port=DEVTOOLS_PORT if port is None else port,
            print=noop_print,
            loop=loop,
        )

    except OSError:
        from rich import print as rprint

        rprint()
        rprint("[bold red]Couldn't start server")
        rprint('Is there another instance of [reverse]textual console[/] running?')


def _make_devtools_aiohttp_app(
    size_change_poll_delay_secs: float = DEFAULT_SIZE_CHANGE_POLL_DELAY_SECONDS,
    port: int | None = None,
    verbose: bool = False,
    exclude: list[str] | None = None,
) -> Application:
    app = Application()

    app.on_shutdown.append(_on_shutdown)
    app.on_startup.append(_on_startup)

    app['verbose'] = verbose
    app['service'] = DevtoolsService(
        update_frequency=size_change_poll_delay_secs,
        port=port,
        verbose=verbose,
        exclude=exclude,
    )

    app.add_routes([
        get('/textual-devtools-websocket', websocket_handler),
    ])

    return app


##


def launch_devtools(
        *,
        verbose: bool = False,
        exclude: list[str] | None = None,
        port: int | None = None,
) -> None:
    from rich.console import Console

    console = Console()
    console.clear()
    console.show_cursor(False)

    try:
        _run_devtools(
            verbose=verbose,
            exclude=exclude,
            port=port,
        )

    finally:
        console.show_cursor(True)


##


def _main() -> None:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('port', type=int, nargs='?', default=DEVTOOLS_PORT)
    parser.add_argument('-v', '--verbose', action='store_true')
    parser.add_argument('-', '--exclude', action='append', help='Exclude log group(s)')

    args = parser.parse_args()

    launch_devtools(
        verbose=bool(args.verbose),
        exclude=args.exclude,
        port=args.port,
    )


if __name__ == '__main__':
    _main()
