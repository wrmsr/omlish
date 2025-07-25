import typing as ta

import h2
import h2.config
import h2.connection
import h2.events
import h2.exceptions
import h2.settings
import hpack
import priority

from omlish import check

from ..config import Config
from ..events import Body
from ..events import Closed
from ..events import Data
from ..events import EndBody
from ..events import EndData
from ..events import InformationalResponse
from ..events import ProtocolEvent
from ..events import RawData
from ..events import Request
from ..events import Response
from ..events import ServerEvent
from ..events import StreamClosed
from ..events import Updated
from ..headers import filter_pseudo_headers
from ..headers import response_headers
from ..streams.httpstream import HttpStream
from ..streams.wsstream import WsStream
from ..taskspawner import TaskSpawner
from ..types import AppWrapper
from ..types import WaitableEvent
from ..workercontext import WorkerContext
from .types import Protocol


##


BUFFER_HIGH_WATER = 2 * 2**14  # Twice the default max frame size (two frames worth)
BUFFER_LOW_WATER = BUFFER_HIGH_WATER / 2


class BufferCompleteError(Exception):
    pass


class StreamBuffer:
    def __init__(self, event_class: type[WaitableEvent]) -> None:
        super().__init__()
        self.buffer = bytearray()
        self._complete = False
        self._is_empty = event_class()
        self._paused = event_class()

    async def drain(self) -> None:
        await self._is_empty.wait()

    def set_complete(self) -> None:
        self._complete = True

    async def close(self) -> None:
        self._complete = True
        self.buffer = bytearray()
        await self._is_empty.set()
        await self._paused.set()

    @property
    def complete(self) -> bool:
        return self._complete and len(self.buffer) == 0

    async def push(self, data: bytes) -> None:
        if self._complete:
            raise BufferCompleteError
        self.buffer.extend(data)
        await self._is_empty.clear()
        if len(self.buffer) >= BUFFER_HIGH_WATER:
            await self._paused.wait()
            await self._paused.clear()

    async def pop(self, max_length: int) -> bytes:
        length = min(len(self.buffer), max_length)
        data = bytes(self.buffer[:length])
        del self.buffer[:length]
        if len(data) < BUFFER_LOW_WATER:
            await self._paused.set()
        if len(self.buffer) == 0:
            await self._is_empty.set()
        return data


class H2Protocol(Protocol):
    def __init__(
        self,
        app: AppWrapper,
        config: Config,
        context: WorkerContext,
        task_spawner: TaskSpawner,
        client: tuple[str, int] | None,
        server: tuple[str, int] | None,
        send: ta.Callable[[ServerEvent], ta.Awaitable[None]],
    ) -> None:
        super().__init__()

        self.app = app
        self.client = client
        self.closed = False
        self.config = config
        self.context = context
        self.task_spawner = task_spawner

        self.connection = h2.connection.H2Connection(
            config=h2.config.H2Configuration(client_side=False, header_encoding=None),
        )
        self.connection.DEFAULT_MAX_INBOUND_FRAME_SIZE = config.h2_max_inbound_frame_size
        self.connection.local_settings = h2.settings.Settings(
            client=False,
            initial_values={
                h2.settings.SettingCodes.MAX_CONCURRENT_STREAMS: config.h2_max_concurrent_streams,
                h2.settings.SettingCodes.MAX_HEADER_LIST_SIZE: config.h2_max_header_list_size,
                h2.settings.SettingCodes.ENABLE_CONNECT_PROTOCOL: 1,
            },
        )

        self.keep_alive_requests = 0
        self.send = send
        self.server = server
        self.streams: dict[int, HttpStream | WsStream] = {}
        # The below are used by the sending task
        self.has_data = self.context.event_class()
        self.priority = priority.PriorityTree()
        self.stream_buffers: dict[int, StreamBuffer] = {}

    @property
    def idle(self) -> bool:
        return len(self.streams) == 0 or all(stream.idle for stream in self.streams.values())

    async def initiate(
        self,
            headers: list[tuple[bytes, bytes]] | None = None,
            settings: str | None = None,
    ) -> None:
        if settings is not None:
            self.connection.initiate_upgrade_connection(
                settings.encode('ascii') if settings is not None else None,
            )
        else:
            self.connection.initiate_connection()

        await self._flush()

        if headers is not None:
            event = h2.events.RequestReceived()
            event.stream_id = 1
            event.headers = [hpack.HeaderTuple(*t) for t in headers]
            await self._create_stream(event)
            await self.streams[event.stream_id].handle(EndBody(stream_id=event.stream_id))

        self.task_spawner.spawn(self.send_task)

    async def send_task(self) -> None:
        # This should be run in a seperate task to the rest of this class. This allows it seperately choose when to
        # send, crucially in what order.
        while not self.closed:
            try:
                stream_id = next(self.priority)
            except priority.DeadlockError:
                await self.has_data.wait()
                await self.has_data.clear()
            else:
                await self._send_data(stream_id)

    async def _send_data(self, stream_id: int) -> None:
        try:
            chunk_size = min(
                self.connection.local_flow_control_window(stream_id),
                self.connection.max_outbound_frame_size,
            )
            chunk_size = max(0, chunk_size)
            data = await self.stream_buffers[stream_id].pop(chunk_size)
            if data:
                self.connection.send_data(stream_id, data)
                await self._flush()
            else:
                self.priority.block(stream_id)

            if self.stream_buffers[stream_id].complete:
                self.connection.end_stream(stream_id)
                await self._flush()
                del self.stream_buffers[stream_id]
                self.priority.remove_stream(stream_id)

        except (h2.exceptions.StreamClosedError, KeyError, h2.exceptions.ProtocolError):
            # Stream or connection has closed whilst waiting to send data, not a problem - just force close it.
            await self.stream_buffers[stream_id].close()
            del self.stream_buffers[stream_id]
            self.priority.remove_stream(stream_id)

    async def handle(self, event: ServerEvent) -> None:
        if isinstance(event, RawData):
            try:
                events = self.connection.receive_data(event.data)
            except h2.exceptions.ProtocolError:
                await self._flush()
                await self.send(Closed())
            else:
                await self._handle_events(events)

        elif isinstance(event, Closed):
            self.closed = True
            stream_ids = list(self.streams.keys())
            for stream_id in stream_ids:
                await self._close_stream(stream_id)
            await self.has_data.set()

    async def stream_send(self, event: ProtocolEvent) -> None:
        try:
            if isinstance(event, (InformationalResponse, Response)):
                self.connection.send_headers(
                    event.stream_id,
                    [
                        (b':status', b'%d' % event.status_code),
                        *event.headers,
                        *response_headers(self.config, 'h2'),
                    ],
                )
                await self._flush()

            elif isinstance(event, (Body, Data)):
                self.priority.unblock(event.stream_id)
                await self.has_data.set()
                await self.stream_buffers[event.stream_id].push(event.data)

            elif isinstance(event, (EndBody, EndData)):
                self.stream_buffers[event.stream_id].set_complete()
                self.priority.unblock(event.stream_id)
                await self.has_data.set()
                await self.stream_buffers[event.stream_id].drain()

            elif isinstance(event, StreamClosed):
                await self._close_stream(event.stream_id)
                idle = len(self.streams) == 0 or all(
                    stream.idle for stream in self.streams.values()
                )
                if idle and self.context.terminated.is_set():
                    self.connection.close_connection()
                    await self._flush()
                await self.send(Updated(idle=idle))

            elif isinstance(event, Request):
                await self._create_server_push(event.stream_id, event.raw_path, event.headers)

        except (
            BufferCompleteError,
            KeyError,
            priority.MissingStreamError,
            h2.exceptions.ProtocolError,
        ):
            # Connection has closed whilst blocked on flow control or connection has advanced ahead of the last emitted
            # event.
            return

    async def _handle_events(self, events: list[h2.events.Event]) -> None:
        for event in events:
            if isinstance(event, h2.events.RequestReceived):
                if self.context.terminated.is_set():
                    self.connection.reset_stream(check.not_none(event.stream_id))
                    self.connection.update_settings(
                        {h2.settings.SettingCodes.MAX_CONCURRENT_STREAMS: 0},
                    )
                else:
                    await self._create_stream(event)
                    await self.send(Updated(idle=False))

                if self.keep_alive_requests > self.config.keep_alive_max_requests:
                    self.connection.close_connection()

            elif isinstance(event, h2.events.DataReceived):
                await self.streams[check.not_none(event.stream_id)].handle(Body(
                    stream_id=check.not_none(event.stream_id),
                    data=check.not_none(event.data),
                ))
                self.connection.acknowledge_received_data(
                    check.not_none(event.flow_controlled_length),
                    check.not_none(event.stream_id),
                )

            elif isinstance(event, h2.events.StreamEnded):
                await self.streams[check.not_none(event.stream_id)].handle(
                    EndBody(stream_id=check.not_none(event.stream_id)),
                )

            elif isinstance(event, h2.events.StreamReset):
                await self._close_stream(check.not_none(event.stream_id))
                await self._window_updated(event.stream_id)

            elif isinstance(event, h2.events.WindowUpdated):
                await self._window_updated(check.not_none(event.stream_id))

            elif isinstance(event, h2.events.PriorityUpdated):
                await self._priority_updated(event)

            elif isinstance(event, h2.events.RemoteSettingsChanged):
                if h2.settings.SettingCodes.INITIAL_WINDOW_SIZE in event.changed_settings:
                    await self._window_updated(None)

            elif isinstance(event, h2.events.ConnectionTerminated):
                await self.send(Closed())

        await self._flush()

    async def _flush(self) -> None:
        data = self.connection.data_to_send()
        if data != b'':
            await self.send(RawData(data=data))

    async def _window_updated(self, stream_id: int | None) -> None:
        if stream_id is None or stream_id == 0:
            # Unblock all streams
            for buf_stream_id in list(self.stream_buffers.keys()):
                self.priority.unblock(buf_stream_id)
        elif stream_id is not None and stream_id in self.stream_buffers:
            self.priority.unblock(stream_id)
        await self.has_data.set()

    async def _priority_updated(self, event: h2.events.PriorityUpdated) -> None:
        stream_id = check.not_none(event.stream_id)

        try:
            self.priority.reprioritize(
                stream_id=stream_id,
                depends_on=event.depends_on or None,
                weight=check.not_none(event.weight),
                exclusive=check.not_none(event.exclusive),
            )

        except priority.MissingStreamError:
            # Received PRIORITY frame before HEADERS frame
            self.priority.insert_stream(
                stream_id=stream_id,
                depends_on=event.depends_on or None,
                weight=check.not_none(event.weight),
                exclusive=check.not_none(event.exclusive),
            )
            self.priority.block(stream_id)

        await self.has_data.set()

    async def _create_stream(self, request: h2.events.RequestReceived) -> None:
        method: str | None = None
        for name, value in request.headers or []:
            if name == b':method':
                method = value.decode('ascii').upper()
            elif name == b':path':
                raw_path = value

        method = check.not_none(method)
        stream_id = check.not_none(request.stream_id)

        if method == 'CONNECT':
            self.streams[stream_id] = WsStream(
                self.app,
                self.config,
                self.context,
                self.task_spawner,
                self.client,
                self.server,
                self.stream_send,
                stream_id,
            )

        else:
            self.streams[stream_id] = HttpStream(
                self.app,
                self.config,
                self.context,
                self.task_spawner,
                self.client,
                self.server,
                self.stream_send,
                stream_id,
            )

        self.stream_buffers[stream_id] = StreamBuffer(self.context.event_class)

        try:
            self.priority.insert_stream(check.not_none(request.stream_id))
        except priority.DuplicateStreamError:
            # Recieved PRIORITY frame before HEADERS frame
            pass
        else:
            self.priority.block(check.not_none(request.stream_id))

        await self.streams[stream_id].handle(Request(
            stream_id=stream_id,
            headers=filter_pseudo_headers(check.not_none(request.headers)),  # type: ignore[arg-type]
            http_version='2',
            method=method,
            raw_path=raw_path,
        ))

        self.keep_alive_requests += 1
        await self.context.mark_request()

    async def _create_server_push(
        self,
            stream_id: int,
            path: bytes,
            headers: list[tuple[bytes, bytes]],
    ) -> None:
        push_stream_id = self.connection.get_next_available_stream_id()
        request_headers = [(b':method', b'GET'), (b':path', path)]
        request_headers.extend(headers)
        request_headers.extend(response_headers(self.config, 'h2'))

        try:
            self.connection.push_stream(
                stream_id=stream_id,
                promised_stream_id=push_stream_id,
                request_headers=request_headers,
            )
            await self._flush()

        except h2.exceptions.ProtocolError:
            # Client does not accept push promises or we are trying to push on a push promises request.
            pass

        else:
            event = h2.events.RequestReceived()
            event.stream_id = push_stream_id
            event.headers = [hpack.HeaderTuple(*t) for t in request_headers]
            await self._create_stream(event)
            await self.streams[event.stream_id].handle(EndBody(stream_id=event.stream_id))
            self.keep_alive_requests += 1

    async def _close_stream(self, stream_id: int) -> None:
        if stream_id in self.streams:
            stream = self.streams.pop(stream_id)
            await stream.handle(StreamClosed(stream_id=stream_id))
            await self.has_data.set()
