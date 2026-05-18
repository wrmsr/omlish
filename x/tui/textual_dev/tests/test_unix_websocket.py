import asyncio
import inspect
import io
import os
import tempfile

from rich.console import Console

from x.tui.textual_dev.client import DevtoolsClient
from x.tui.textual_dev.client import DevtoolsLog
from x.tui.textual_dev.server import DEFAULT_SIZE_CHANGE_POLL_DELAY_SECONDS
from x.tui.textual_dev.server import make_devtools_pipeline_spec
from x.tui.textual_dev.service import DevtoolsService


async def _test_devtools_unix_websocket_roundtrip(socket_path: str) -> None:
    output = io.StringIO()
    console = Console(file=output, width=80, height=24, force_terminal=False)

    service = DevtoolsService(
        update_frequency=DEFAULT_SIZE_CHANGE_POLL_DELAY_SECONDS,
        console=console,
    )

    async def handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        await service.handle(reader, writer, make_devtools_pipeline_spec)

    await service.start()
    server = await asyncio.start_unix_server(handle_client, path=socket_path)

    async with server:
        client = DevtoolsClient(socket_path=socket_path)
        try:
            await client.connect()

            assert client.is_connected
            assert client.console.width == 80
            assert client.console.height == 24

            caller = inspect.Traceback(
                filename='demo.py',
                lineno=7,
                function='demo',
                code_context=None,
                index=None,
            )
            client.log(DevtoolsLog('hello devtools', caller))

            for _ in range(50):
                await asyncio.sleep(0.02)
                if 'hello devtools' in output.getvalue():
                    break
            assert 'hello devtools' in output.getvalue()

        finally:
            await client.disconnect()
            await service.shutdown()


def test_devtools_unix_websocket_roundtrip(tmp_path) -> None:
    socket_path = os.path.join(tempfile.mkdtemp(), 'devtools.sock')
    asyncio.run(_test_devtools_unix_websocket_roundtrip(socket_path))
