import asyncio
import json
import time
import typing as ta

from rich.console import Console
from rich.markup import escape
from textual._log import LogGroup

from omcore.http.pipelines.websockets.objects import IoPipelineWebsocketClose
from omcore.http.pipelines.websockets.objects import IoPipelineWebsocketOpen
from omcore.http.pipelines.websockets.objects import IoPipelineWebsocketText
from omcore.io.pipelines.core import IoPipelineHandler
from omcore.io.pipelines.core import IoPipelineHandlerContext
from omcore.io.pipelines.core import IoPipelineMessages
from omcore.io.pipelines.drivers.asyncio import PollAsyncioStreamIoPipelineDriver

from .protocol import DevtoolsWebsocketSend
from .protocol import decode_message
from .protocol import decode_segments
from .protocol import encode_message
from .renderables import DevConsoleHeader
from .renderables import DevConsoleLog
from .renderables import DevConsoleNotice


##


QUEUEABLE_TYPES = {'client_log', 'client_spillover'}


class DevtoolsServerWebsocketHandler(IoPipelineHandler):
    def __init__(self, client: ClientHandler) -> None:
        super().__init__()

        self._client = client

    def inbound(self, ctx: IoPipelineHandlerContext, msg: ta.Any) -> None:
        if isinstance(msg, DevtoolsWebsocketSend):
            ctx.feed_out(msg.message)
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


class DevtoolsService:
    """
    A running instance of devtools has a single DevtoolsService which is responsible for tracking connected client
    applications.
    """

    def __init__(
        self,
        update_frequency: float,
        port: int | None = None,
        verbose: bool = False,
        exclude: list[str] | None = None,
        console: Console | None = None,
    ) -> None:
        """
        Args:
            update_frequency: The number of seconds to wait between sending updates of the console size to connected
                clients.
            port: The port the devtools server is running on.
            verbose: Enable verbose logging on client.
            exclude: List of log groups to exclude from output.
        """

        super().__init__()

        self.update_frequency = update_frequency
        self.port = port
        self.verbose = verbose
        self.exclude = {name.upper() for name in exclude} if exclude else set()
        self.console = Console() if console is None else console
        self.shutdown_event = asyncio.Event()
        self.clients: list[ClientHandler] = []

    async def start(self) -> None:
        """Starts devtools tasks"""

        self.size_poll_task = asyncio.create_task(self._console_size_poller())
        self.console.print(DevConsoleHeader(port=self.port, verbose=self.verbose))

    @property
    def clients_connected(self) -> bool:
        """Returns True if there are connected clients, False otherwise."""

        return len(self.clients) > 0

    async def _console_size_poller(self) -> None:
        """
        Poll console dimensions, and add a `server_info` message to the Queue any time a change occurs. We only poll if
        there are clients connected, and if we're not shutting down the server.
        """

        current_width = self.console.width
        current_height = self.console.height

        await self._send_server_info_to_all()

        while not self.shutdown_event.is_set():
            width = self.console.width
            height = self.console.height
            dimensions_changed = width != current_width or height != current_height
            if dimensions_changed:
                await self._send_server_info_to_all()
                current_width = width
                current_height = height

            try:
                await asyncio.wait_for(
                    self.shutdown_event.wait(),
                    timeout=self.update_frequency,
                )

            except TimeoutError:
                pass

    async def _send_server_info_to_all(self) -> None:
        """Add `server_info` message to the queues of every client"""

        for client_handler in self.clients:
            await self.send_server_info(client_handler)

    async def send_server_info(self, client_handler: ClientHandler) -> None:
        """
        Send information about the server e.g. width and height of Console to a connected client.

        Args:
            client_handler: The client to send information to
        """

        await client_handler.send_message({
            'type': 'server_info',
            'payload': {
                'width': self.console.width,
                'height': self.console.height,
                'verbose': self.verbose,
            },
        })

    async def handle(
            self,
            reader: asyncio.StreamReader,
            writer: asyncio.StreamWriter,
            pipeline_spec_factory: ta.Callable[[ClientHandler], ta.Any],
    ) -> None:
        """Handles a single client connection."""

        client = ClientHandler(service=self)
        try:
            await client.run(reader, writer, pipeline_spec_factory(client))
        finally:
            if client in self.clients:
                self.clients.remove(client)

    async def shutdown(self) -> None:
        """Stop server async tasks and clean up all client handlers"""

        # Stop polling/writing Console dimensions to clients
        self.shutdown_event.set()
        await self.size_poll_task

        # We're shutting down the server, so inform all connected clients
        for client in self.clients:
            await client.close()
        self.clients.clear()


class ClientHandler:
    """
    Handles a single client connection to the devtools. A single DevtoolsService manages many ClientHandlers. A single
    ClientHandler corresponds to a single running Textual application instance, and is responsible for communication
    with that Textual app.
    """

    def __init__(self, service: DevtoolsService) -> None:
        """
        Args:
            service: The parent DevtoolsService which is responsible for the handling of this client.
        """

        super().__init__()

        self.service = service
        self.driver: PollAsyncioStreamIoPipelineDriver | None = None
        self.opened = False

    async def send_message(self, message: dict[str, object]) -> None:
        """
        Send a message to a client

        Args:
            message: The dict which will be sent to the client.
        """

        if self.driver is not None:
            self.driver.enqueue(DevtoolsWebsocketSend(encode_message(message)))

    async def _consume_outgoing(self) -> None:
        """Consume messages from the outgoing (server -> client) Queue."""

        while True:
            message_json = await self.outgoing_queue.get()
            if message_json is None:
                self.outgoing_queue.task_done()
                break

            if self.driver is not None:
                self.driver.enqueue(DevtoolsWebsocketSend(encode_message(message_json)))

            self.outgoing_queue.task_done()

    async def _consume_incoming(self) -> None:
        """
        Consume messages from the incoming (client -> server) Queue, and print the corresponding renderables to the
        console for each message.
        """

        last_message_time: float | None = None
        while True:
            message = await self.incoming_queue.get()
            if message is None:
                self.incoming_queue.task_done()
                break

            message_type = message['type']
            if message_type == 'client_log':
                payload = message['payload']
                if LogGroup(payload.get('group', 0)).name in self.service.exclude:
                    continue

                segments = decode_segments(payload['segments'])

                message_time = time.monotonic()
                if (
                        last_message_time is not None and
                        message_time - last_message_time > 0.5
                ):
                    # Print a rule if it has been longer than half a second since the last message
                    self.service.console.rule()

                self.service.console.print(
                    DevConsoleLog(
                        segments=segments,
                        path=payload['path'],
                        line_number=payload['line_number'],
                        unix_timestamp=payload['timestamp'],
                        group=payload.get('group', 0),
                        verbosity=payload.get('verbosity', 0),
                        severity=payload.get('severity', 0),
                    ),
                )
                last_message_time = message_time

            elif message_type == 'client_spillover':
                spillover = int(message['payload']['spillover'])
                info_renderable = DevConsoleNotice(
                    f'Discarded {spillover} messages',
                    level='warning',
                )
                self.service.console.print(info_renderable)

            self.incoming_queue.task_done()

    incoming_queue: asyncio.Queue[dict[str, ta.Any] | None]
    outgoing_queue: asyncio.Queue[dict[str, ta.Any] | None]
    incoming_messages_task: asyncio.Task

    async def run(
            self,
            reader: asyncio.StreamReader,
            writer: asyncio.StreamWriter,
            pipeline_spec: ta.Any,
    ) -> None:
        """Prepare the websocket and communication queues, and continuously read messages from the queues."""

        self.incoming_queue = asyncio.Queue()
        self.outgoing_queue = asyncio.Queue()
        self.incoming_messages_task = asyncio.create_task(self._consume_incoming())

        self.driver = PollAsyncioStreamIoPipelineDriver(pipeline_spec, reader, writer)

        try:
            await self.driver.loop_until_done()

        except Exception as error:  # noqa
            self.service.console.print(DevConsoleNotice(str(error), level='error'))

        finally:
            if self.opened:
                self.service.console.print(
                    '\n',
                    DevConsoleNotice('Client disconnected'),
                )

            await self.close()

    async def close(self) -> None:
        """
        Stop all incoming/outgoing message processing, and shutdown the websocket connection associated with this
        client.
        """

        saw_final_output = True
        if self.driver is not None:
            try:
                saw_final_output = self.driver.pipeline.saw_final_output
            except AttributeError:
                saw_final_output = False

        if self.driver is not None and not saw_final_output:
            try:
                self.driver.enqueue(DevtoolsWebsocketSend(IoPipelineWebsocketClose()))
                self.driver.enqueue(DevtoolsWebsocketSend(IoPipelineMessages.FinalOutput()))
            except Exception:  # noqa
                pass

        if hasattr(self, 'incoming_queue'):
            await self.incoming_queue.put(None)
        if hasattr(self, 'incoming_messages_task'):
            await asyncio.shield(self.incoming_messages_task)

    def on_open(self) -> None:
        self.opened = True
        self.service.clients.append(self)
        self.service.console.print(DevConsoleNotice('Client connected'))

        if self.driver is not None:
            self.driver.enqueue(DevtoolsWebsocketSend(encode_message({
                'type': 'server_info',
                'payload': {
                    'width': self.service.console.width,
                    'height': self.service.console.height,
                    'verbose': self.service.verbose,
                },
            })))

    def on_message(self, message: IoPipelineWebsocketText) -> None:
        try:
            message_json = decode_message(message)
        except (TypeError, json.JSONDecodeError):
            self.service.console.print(escape(message.text))
            return

        message_type = message_json.get('type')
        if not message_type:
            return
        if (
                message_type in QUEUEABLE_TYPES and
                not self.service.shutdown_event.is_set()
        ):
            self.incoming_queue.put_nowait(message_json)
