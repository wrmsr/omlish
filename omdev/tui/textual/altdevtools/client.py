import asyncio
import inspect
import io
import os
import time
import typing as ta

from rich.console import Console
from rich.segment import Segment
from textual._log import LogGroup
from textual._log import LogVerbosity
from textual.constants import DEVTOOLS_PORT

from omcore.http.headers import HttpHeaders
from omcore.http.pipelines.clients.requests import IoPipelineHttpRequestEncoder
from omcore.http.pipelines.clients.responses import IoPipelineHttpResponseDecoder
from omcore.http.pipelines.requests import IoPipelineHttpRequestHead
from omcore.http.pipelines.websockets.aggregators import IoPipelineWebsocketAggregator
from omcore.http.pipelines.websockets.frames import IoPipelineWebsocketClientFrameDecoder
from omcore.http.pipelines.websockets.frames import IoPipelineWebsocketClientFrameEncoder
from omcore.http.pipelines.websockets.handshakes import IoPipelineWebsocketClientUpgradeHandler
from omcore.http.pipelines.websockets.objects import IoPipelineWebsocketClose
from omcore.http.pipelines.websockets.objects import IoPipelineWebsocketOpen
from omcore.http.pipelines.websockets.objects import IoPipelineWebsocketText
from omcore.http.versions import HttpVersions
from omcore.io.pipelines.core import IoPipeline
from omcore.io.pipelines.core import IoPipelineHandler
from omcore.io.pipelines.core import IoPipelineHandlerContext
from omcore.io.pipelines.core import IoPipelineMessages
from omcore.io.pipelines.drivers.asyncio import PollAsyncioStreamIoPipelineDriver

from .protocol import DevtoolsWebsocketSend
from .protocol import decode_message
from .protocol import encode_message
from .protocol import encode_segments


##


READY_TIMEOUT = 0.5
LOG_QUEUE_MAXSIZE = 512


class DevtoolsLog(ta.NamedTuple):
    """
    A devtools log message.

    Attributes:
        objects_or_string: Corresponds to the data that will ultimately be passed to Console.print in order to generate
            the log Segments.
        caller: Information about where this log message was created. In other words, where did the user call `print` or
            `App.log` from. Used to display line number and file name in the devtools window.
    """

    objects_or_string: tuple[ta.Any, ...] | str
    caller: inspect.Traceback


class DevtoolsConsole(Console):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.record = True

    def export_segments(self) -> list[Segment]:
        """
        Return the list of Segments that have be printed using this console

        Returns:
            The list of Segments that have been printed using this console
        """

        with self._record_buffer_lock:
            segments = self._record_buffer[:]
            self._record_buffer.clear()
        return segments


class DevtoolsConnectionError(Exception):
    """Raise when the devtools client is unable to connect to the server"""


class ClientShutdown:
    """Sentinel type sent to client queue(s) to indicate shutdown"""


class DevtoolsClientWebsocketHandler(IoPipelineHandler):
    def __init__(self, client: DevtoolsClient) -> None:
        super().__init__()

        self._client = client

    def inbound(self, ctx: IoPipelineHandlerContext, msg: ta.Any) -> None:
        if isinstance(msg, DevtoolsWebsocketSend):
            ctx.feed_out(msg.message)
            return

        if isinstance(msg, IoPipelineMessages.InitialInput):
            ctx.feed_in(msg)
            ctx.feed_out(IoPipelineHttpRequestHead(
                method='GET',
                target='/textual-devtools-websocket',
                version=HttpVersions.HTTP_1_1,
                headers=HttpHeaders([
                    ('Host', 'localhost'),
                ]),
            ))
            return

        if isinstance(msg, IoPipelineWebsocketOpen):
            self._client.on_open()
            return

        if isinstance(msg, IoPipelineWebsocketText):
            self._client.on_message(msg)
            return

        if isinstance(msg, (IoPipelineWebsocketClose, IoPipelineMessages.FinalInput)):
            ctx.feed_out(IoPipelineMessages.FinalOutput())
            return

        ctx.feed_in(msg)


class DevtoolsClient:
    """
    Client responsible for websocket communication with the devtools server. Communicates using a simple JSON protocol.

    Messages have the format `{"type": <str>, "payload": <json>}`.

    Valid values for `"type"` (that can be sent from client -> server) are `"client_log"` (for log messages) and
    `"client_spillover"` (for reporting to the server that messages were discarded due to rate limiting).

    A `"client_log"` message has a `"payload"` format as follows:
    ```
    {"timestamp": <int, unix timestamp>,
     "path": <str, path of file>,
     "line_number": <int, line number log was made from>,
     "encoded_segments": <str, pickled then b64 encoded Segments to log>}
    ```

    A `"client_spillover"` message has a `"payload"` format as follows:
    ```
    {"spillover": <int, the number of messages discarded by rate-limiting>}
    ```

    Args:
        host: The host the devtools server is running on, defaults to "127.0.0.1"
        port: The port the devtools server is accessed via, `texDEVTOOLS_PORT` by default.
    """

    def __init__(
            self,
            host: str = '127.0.0.1',
            port: int | None = None,
            *,
            socket_path: str | None = None,
    ) -> None:
        super().__init__()

        if port is None:
            port = DEVTOOLS_PORT
        self.host = host
        self.port = port
        self.socket_path = socket_path or os.environ.get('TEXTUAL_DEVTOOLS_SOCKET_PATH')
        self.log_queue_task: asyncio.Task | None = None
        self.console: DevtoolsConsole = DevtoolsConsole(file=io.StringIO())
        self.driver: PollAsyncioStreamIoPipelineDriver | None = None
        self.driver_task: asyncio.Task | None = None
        self.log_queue: asyncio.Queue[dict[str, ta.Any] | type[ClientShutdown]] | None = None
        self.spillover: int = 0
        self.verbose: bool = False
        self._ready_event: asyncio.Event = asyncio.Event()
        self._connected = False

    async def connect(self) -> None:
        """
        Connect to the devtools server.

        Raises:
            DevtoolsConnectionError: If we're unable to establish a connection to the server for any reason.
        """

        self.log_queue = asyncio.Queue(maxsize=LOG_QUEUE_MAXSIZE)
        if self.socket_path is None:
            raise DevtoolsConnectionError

        try:
            reader, writer = await asyncio.open_unix_connection(self.socket_path)
        except OSError:
            raise DevtoolsConnectionError from None

        log_queue = self.log_queue
        self.driver = PollAsyncioStreamIoPipelineDriver(
            IoPipeline.Spec([
                IoPipelineHttpResponseDecoder(),
                IoPipelineHttpRequestEncoder(),
                IoPipelineWebsocketClientUpgradeHandler(host='localhost'),
                IoPipelineWebsocketClientFrameDecoder(),
                IoPipelineWebsocketClientFrameEncoder(),
                IoPipelineWebsocketAggregator(),
                DevtoolsClientWebsocketHandler(self),
            ]),
            reader,
            writer,
        )

        async def send_queued_logs() -> None:
            """
            Coroutine function which is scheduled as a Task, which consumes messages from the log queue and sends them
            to the server via websocket.
            """

            while True:
                log = await log_queue.get()
                if log is ClientShutdown:
                    log_queue.task_done()
                    break
                if self.driver is not None:
                    self.driver.enqueue(DevtoolsWebsocketSend(encode_message(ta.cast(dict[str, ta.Any], log))))
                log_queue.task_done()

        async def server_info_received() -> None:
            """Wait for the first server info message to be received and handled."""

            try:
                await asyncio.wait_for(self._ready_event.wait(), timeout=READY_TIMEOUT)
            except TimeoutError:
                return

        self.driver_task = asyncio.create_task(self.driver.loop_until_done())
        self.log_queue_task = asyncio.create_task(send_queued_logs())

        await server_info_received()

    async def _stop_log_queue_processing(self) -> None:
        """
        Schedule end of processing of the log queue, meaning that any messages a user logs will be added to the queue,
        but not consumed and sent to the server.
        """

        if self.log_queue is not None:
            await self.log_queue.put(ClientShutdown)
        if self.log_queue_task:
            await self.log_queue_task

    async def _stop_incoming_message_processing(self) -> None:
        """
        Schedule stop of the task which listens for incoming messages from the server around changes in the server
        console size.
        """

        if self.driver is not None:
            try:
                self.driver.enqueue(DevtoolsWebsocketSend(IoPipelineWebsocketClose()))
                self.driver.enqueue(DevtoolsWebsocketSend(IoPipelineMessages.FinalOutput()))
            except Exception:  # noqa
                pass
        if self.driver_task:
            await self.driver_task
        self._connected = False

    async def disconnect(self) -> None:
        """Disconnect from the devtools server by stopping tasks and closing connections."""

        await self._stop_log_queue_processing()
        await self._stop_incoming_message_processing()

    @property
    def is_connected(self) -> bool:
        """
        Checks connection to devtools server.

        Returns:
            True if this host is connected to the server. False otherwise.
        """

        return self._connected

    def log(
        self,
        log: DevtoolsLog,
        group: LogGroup = LogGroup.UNDEFINED,
        verbosity: LogVerbosity = LogVerbosity.NORMAL,
    ) -> None:
        """Queue a log to be sent to the devtools server for display."""

        if isinstance(log.objects_or_string, str):
            self.console.print(log.objects_or_string, markup=False)
        else:
            self.console.print(*log.objects_or_string, markup=False)

        segments = self.console.export_segments()

        message: dict[str, ta.Any] = {
            'type': 'client_log',
            'payload': {
                'group': group.value,
                'verbosity': verbosity.value,
                'timestamp': int(time.time()),
                'path': getattr(log.caller, 'filename', ''),
                'line_number': getattr(log.caller, 'lineno', 0),
                'segments': self._encode_segments(segments),
            },
        }

        try:
            if self.log_queue:
                self.log_queue.put_nowait(message)
                if self.spillover > 0 and self.log_queue.qsize() < LOG_QUEUE_MAXSIZE:
                    # Tell the server how many messages we had to discard due to the log queue filling to capacity on
                    # the client.
                    spillover_message = {
                        'type': 'client_spillover',
                        'payload': {
                            'spillover': self.spillover,
                        },
                    }
                    self.log_queue.put_nowait(spillover_message)
                    self.spillover = 0
        except asyncio.QueueFull:
            self.spillover += 1

    @classmethod
    def _encode_segments(cls, segments: list[Segment]) -> str:
        """
        Pickle a list of Segments

        Args:
            segments: A list of Segments to encode

        Returns:
            The Segment list pickled with the latest protocol.
        """

        return encode_segments(segments)

    def on_open(self) -> None:
        self._connected = True

    def on_message(self, message: IoPipelineWebsocketText) -> None:
        message_json = decode_message(message)
        if message_json['type'] == 'server_info':
            payload = message_json['payload']
            self.console.width = payload['width']
            self.console.height = payload['height']
            self.verbose = payload.get('verbose', False)
            self._ready_event.set()
