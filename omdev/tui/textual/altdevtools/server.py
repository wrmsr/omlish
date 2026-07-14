import asyncio
import contextlib
import os
import tempfile
import typing as ta

from textual.constants import DEVTOOLS_PORT

from omcore.http.pipelines.servers.requests import IoPipelineHttpRequestDecoder
from omcore.http.pipelines.servers.responses import IoPipelineHttpResponseEncoder
from omcore.http.pipelines.websockets.aggregators import IoPipelineWebsocketAggregator
from omcore.http.pipelines.websockets.frames import IoPipelineWebsocketServerFrameDecoder
from omcore.http.pipelines.websockets.frames import IoPipelineWebsocketServerFrameEncoder
from omcore.http.pipelines.websockets.handshakes import IoPipelineWebsocketServerUpgradeHandler
from omcore.io.pipelines.core import IoPipeline

from .service import DevtoolsServerWebsocketHandler
from .service import DevtoolsService


##


DEFAULT_SIZE_CHANGE_POLL_DELAY_SECONDS = 2


def make_devtools_pipeline_spec(client_handler: ta.Any) -> IoPipeline.Spec:
    return IoPipeline.Spec([
        IoPipelineHttpRequestDecoder(),
        IoPipelineHttpResponseEncoder(),
        IoPipelineWebsocketServerUpgradeHandler(),
        IoPipelineWebsocketServerFrameDecoder(),
        IoPipelineWebsocketServerFrameEncoder(),
        IoPipelineWebsocketAggregator(),
        DevtoolsServerWebsocketHandler(client_handler),
    ])


def _default_socket_path(port: int | None = None) -> str:
    return os.path.join(tempfile.gettempdir(), f'textual-devtools-{DEVTOOLS_PORT if port is None else port}.sock')


async def a_run_devtools(
        *,
        verbose: bool = False,
        exclude: list[str] | None = None,
        port: int | None = None,
        socket_path: str | None = None,
        size_change_poll_delay_secs: float = DEFAULT_SIZE_CHANGE_POLL_DELAY_SECONDS,
        console: ta.Any = None,
) -> None:
    socket_path = socket_path or _default_socket_path(port)

    service = DevtoolsService(
        update_frequency=size_change_poll_delay_secs,
        port=port,
        verbose=verbose,
        exclude=exclude,
        console=console,
    )

    async def _handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        await service.handle(reader, writer, make_devtools_pipeline_spec)

    with contextlib.suppress(FileNotFoundError):
        os.unlink(socket_path)

    await service.start()
    server = await asyncio.start_unix_server(_handle_client, path=socket_path)

    try:
        async with server:
            await server.serve_forever()
    finally:
        await service.shutdown()
        with contextlib.suppress(FileNotFoundError):
            os.unlink(socket_path)


def _run_devtools(
        *,
        verbose: bool = False,
        exclude: list[str] | None = None,
        port: int | None = None,
        socket_path: str | None = None,
) -> None:
    try:
        asyncio.run(a_run_devtools(
            verbose=verbose,
            exclude=exclude,
            port=port,
            socket_path=socket_path,
        ))

    except OSError:
        from rich import print as rprint

        rprint()
        rprint("[bold red]Couldn't start server")
        rprint('Is there another instance of [reverse]textual console[/] running?')


##


def launch_devtools(
        *,
        verbose: bool = False,
        exclude: list[str] | None = None,
        port: int | None = None,
        socket_path: str | None = None,
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
            socket_path=socket_path,
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
    parser.add_argument('--socket-path')

    args = parser.parse_args()

    launch_devtools(
        verbose=bool(args.verbose),
        exclude=args.exclude,
        port=args.port,
        socket_path=args.socket_path,
    )


if __name__ == '__main__':
    _main()
