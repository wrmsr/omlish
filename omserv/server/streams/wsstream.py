import encodings.idna  # prevents `LookupError: unknown encoding: idna`  # noqa
import enum
import io
import logging
import time
import typing as ta
import urllib.parse

from omlish import check
import wsproto as wsp
import wsproto.events as wse
import wsproto.extensions
import wsproto.frame_protocol
import wsproto.utilities

from ..config import Config
from ..events import Body
from ..events import Data
from ..events import EndBody
from ..events import EndData
from ..events import ProtocolEvent
from ..events import Request
from ..events import Response
from ..events import StreamClosed
from ..taskspawner import TaskSpawner
from ..types import AsgiSendEvent
from ..types import AppWrapper
from ..types import WebsocketAcceptEvent
from ..types import WebsocketResponseBodyEvent
from ..types import WebsocketResponseStartEvent
from ..types import WebsocketScope
from ..workercontext import WorkerContext
from .httpstream import UnexpectedMessageError
from .utils import build_and_validate_headers
from .utils import log_access
from .utils import suppress_body
from .utils import valid_server_name


log = logging.getLogger(__name__)


class AsgiWebsocketState(enum.Enum):
    # Hypercorn supports the Asgi websocket HTTP response extension, which allows HTTP responses rather than acceptance.
    HANDSHAKE = enum.auto()
    CONNECTED = enum.auto()
    RESPONSE = enum.auto()
    CLOSED = enum.auto()
    HTTPCLOSED = enum.auto()


class FrameTooLargeError(Exception):
    pass


class Handshake:
    def __init__(
            self,
            headers: list[tuple[bytes, bytes]],
            http_version: str,
    ) -> None:
        super().__init__()

        self.http_version = http_version
        self.connection_tokens: list[str] | None = None
        self.extensions: list[str] | None = None
        self.key: bytes | None = None
        self.subprotocols: list[str] | None = None
        self.upgrade: bytes | None = None
        self.version: bytes | None = None

        for name, value in headers:
            name = name.lower()

            if name == b'connection':
                self.connection_tokens = wsp.utilities.split_comma_header(value)

            elif name == b'sec-websocket-extensions':
                self.extensions = wsp.utilities.split_comma_header(value)

            elif name == b'sec-websocket-key':
                self.key = value

            elif name == b'sec-websocket-protocol':
                self.subprotocols = wsp.utilities.split_comma_header(value)

            elif name == b'sec-websocket-version':
                self.version = value

            elif name == b'upgrade':
                self.upgrade = value

    def is_valid(self) -> bool:
        if self.http_version < '1.1':
            return False

        elif self.http_version == '1.1':
            if self.key is None:
                return False

            if self.connection_tokens is None or not any(
                token.lower() == 'upgrade' for token in self.connection_tokens
            ):
                return False

            if (self.upgrade or b'').lower() != b'websocket':
                return False

        if self.version != wsp.handshake.WEBSOCKET_VERSION:
            return False

        return True

    def accept(
        self,
        subprotocol: str | None,
        additional_headers: ta.Iterable[tuple[bytes, bytes]],
    ) -> tuple[int, list[tuple[bytes, bytes]], wsp.Connection]:
        headers = []
        if subprotocol is not None:
            if self.subprotocols is None or subprotocol not in self.subprotocols:
                raise Exception('Invalid Subprotocol')
            else:
                headers.append((b'sec-websocket-protocol', subprotocol.encode()))

        extensions: list[wsp.extensions.Extension] = [wsp.extensions.PerMessageDeflate()]
        accepts = None
        if self.extensions is not None:
            accepts = wsp.handshake.server_extensions_handshake(self.extensions, extensions)

        if accepts:
            headers.append((b'sec-websocket-extensions', accepts))

        if self.key is not None:
            headers.append((b'sec-websocket-accept', wsp.utilities.generate_accept_token(self.key)))

        status_code = 200
        if self.http_version == '1.1':
            headers.extend([(b'upgrade', b'WebSocket'), (b'connection', b'Upgrade')])
            status_code = 101

        for name, value in additional_headers:
            if name == b'sec-websocket-protocol' or name.startswith(b':'):
                raise Exception(f'Invalid additional header, {name.decode()}')

            headers.append((name, value))

        return status_code, headers, wsp.Connection(wsp.ConnectionType.SERVER, extensions)


class WebsocketBuffer:
    def __init__(self, max_length: int) -> None:
        super().__init__()

        self.value: io.BytesIO | io.StringIO | None = None
        self.length = 0
        self.max_length = max_length

    def extend(self, event: wse.Message) -> None:
        if self.value is None:
            if isinstance(event, wse.TextMessage):
                self.value = io.StringIO()
            else:
                self.value = io.BytesIO()

        self.length += self.value.write(event.data)

        if self.length > self.max_length:
            raise FrameTooLargeError

    def clear(self) -> None:
        self.value = None
        self.length = 0

    def to_message(self) -> dict:
        return {
            'type': 'websocket.receive',
            'bytes': self.value.getvalue() if isinstance(self.value, io.BytesIO) else None,
            'text': self.value.getvalue() if isinstance(self.value, io.StringIO) else None,
        }


class WsStream:
    def __init__(
        self,
        app: AppWrapper,
        config: Config,
        context: WorkerContext,
        task_spawner: TaskSpawner,
        client: tuple[str, int] | None,
        server: tuple[str, int] | None,
        send: ta.Callable[[ProtocolEvent], ta.Awaitable[None]],
        stream_id: int,
    ) -> None:
        super().__init__()

        self.app = app
        self.app_put: ta.Callable | None = None
        self.buffer = WebsocketBuffer(config.websocket_max_message_size)
        self.client = client
        self.closed = False
        self.config = config
        self.context = context
        self.task_spawner = task_spawner
        self.response: WebsocketResponseStartEvent
        self.scope: WebsocketScope
        self.send = send
        # RFC 8441 for HTTP/2 says use http or https, Asgi says ws or wss
        self.scheme = 'ws'  # #'wss' if ssl else 'ws'
        self.server = server
        self.start_time: float
        self.state = AsgiWebsocketState.HANDSHAKE
        self.stream_id = stream_id

        self.connection: wsp.Connection
        self.handshake: Handshake

    @property
    def idle(self) -> bool:
        return self.state in {AsgiWebsocketState.CLOSED, AsgiWebsocketState.HTTPCLOSED}

    async def handle(self, event: ProtocolEvent) -> None:
        if self.closed:
            return
        elif isinstance(event, Request):
            self.start_time = time.time()
            self.handshake = Handshake(event.headers, event.http_version)
            path, _, query_string = event.raw_path.partition(b'?')
            self.scope = {
                'type': 'websocket',
                'asgi': {'spec_version': '2.3', 'version': '3.0'},
                'scheme': self.scheme,
                'http_version': event.http_version,
                'path': urllib.parse.unquote(path.decode('ascii')),
                'raw_path': path,
                'query_string': query_string,
                # 'root_path': self.config.root_path,
                'client': self.client,
                'server': self.server,
                'subprotocols': self.handshake.subprotocols or [],
                'extensions': {'websocket.http.response': {}},
            }

            if not valid_server_name(self.config, event):
                await self._send_error_response(404)
                self.closed = True

            elif not self.handshake.is_valid():
                await self._send_error_response(400)
                self.closed = True

            else:
                self.app_put = await self.task_spawner.spawn_app(self.app, self.config, self.scope, self.app_send)
                await self.app_put({'type': 'websocket.connect'})

        elif isinstance(event, (Body, Data)):
            self.connection.receive_data(event.data)
            await self._handle_events()

        elif isinstance(event, StreamClosed):
            self.closed = True

            if self.app_put is not None:
                if self.state in {AsgiWebsocketState.HTTPCLOSED, AsgiWebsocketState.CLOSED}:
                    code = wsp.frame_protocol.CloseReason.NORMAL_CLOSURE.value
                else:
                    code = wsp.frame_protocol.CloseReason.ABNORMAL_CLOSURE.value

                await self.app_put({'type': 'websocket.disconnect', 'code': code})

    async def app_send(self, message: AsgiSendEvent | None) -> None:
        if self.closed:
            # Allow app to finish after close
            return

        if message is None:  # Asgi App has finished sending messages
            # Cleanup if required
            if self.state == AsgiWebsocketState.HANDSHAKE:
                await self._send_error_response(500)

                log_access(
                    self.config,
                    self.scope,
                    {'status': 500, 'headers': []},
                    time.time() - self.start_time,
                )

            elif self.state == AsgiWebsocketState.CONNECTED:
                await self._send_wsproto_event(wse.CloseConnection(code=wsp.frame_protocol.CloseReason.INTERNAL_ERROR))

            await self.send(StreamClosed(stream_id=self.stream_id))

        elif message['type'] == 'websocket.accept' and self.state == AsgiWebsocketState.HANDSHAKE:
            await self._accept(message)

        elif (
            message['type'] == 'websocket.http.response.start'
            and self.state == AsgiWebsocketState.HANDSHAKE
        ):
            self.response = message

        elif message['type'] == 'websocket.http.response.body' and self.state in {
            AsgiWebsocketState.HANDSHAKE,
            AsgiWebsocketState.RESPONSE,
        }:
            await self._send_rejection(message)

        elif message['type'] == 'websocket.send' and self.state == AsgiWebsocketState.CONNECTED:
            event: wse.Event
            if message.get('bytes') is not None:
                event = wse.BytesMessage(data=bytes(message['bytes']))

            elif not isinstance(message['text'], str):
                raise TypeError(f'{message["text"]} should be a str')

            else:
                event = wse.TextMessage(data=message['text'])

            await self._send_wsproto_event(event)

        elif (
            message['type'] == 'websocket.close' and self.state == AsgiWebsocketState.HANDSHAKE
        ):
            self.state = AsgiWebsocketState.HTTPCLOSED
            await self._send_error_response(403)

        elif message['type'] == 'websocket.close':
            self.state = AsgiWebsocketState.CLOSED

            await self._send_wsproto_event(wse.CloseConnection(
                code=int(message.get('code', wsp.frame_protocol.CloseReason.NORMAL_CLOSURE)),
                reason=message.get('reason'),
            ))

            await self.send(EndData(stream_id=self.stream_id))

        else:
            raise UnexpectedMessageError(self.state, message['type'])

    async def _handle_events(self) -> None:
        for event in self.connection.events():
            if isinstance(event, wse.Message):
                try:
                    self.buffer.extend(event)
                except FrameTooLargeError:
                    await self._send_wsproto_event(wse.CloseConnection(
                        code=wsp.frame_protocol.CloseReason.MESSAGE_TOO_BIG,
                    ))
                    break

                if event.message_finished:
                    await check.not_none(self.app_put)(self.buffer.to_message())
                    self.buffer.clear()

            elif isinstance(event, wse.Ping):
                await self._send_wsproto_event(event.response())

            elif isinstance(event, wse.CloseConnection):
                if self.connection.state == wsp.ConnectionState.REMOTE_CLOSING:
                    await self._send_wsproto_event(event.response())

                await self.send(StreamClosed(stream_id=self.stream_id))

    async def _send_error_response(self, status_code: int) -> None:
        await self.send(
            Response(
                stream_id=self.stream_id,
                status_code=status_code,
                headers=[(b'content-length', b'0'), (b'connection', b'close')],
            ),
        )
        await self.send(EndBody(stream_id=self.stream_id))
        log_access(
            self.config,
            self.scope,
            {
                'status': status_code,
                'headers': [],
            },
            time.time() - self.start_time,
        )

    async def _send_wsproto_event(self, event: wse.Event) -> None:
        try:
            data = self.connection.send(event)
        except wsp.utilities.LocalProtocolError:
            pass
        else:
            await self.send(Data(stream_id=self.stream_id, data=data))

    async def _accept(self, message: WebsocketAcceptEvent) -> None:
        self.state = AsgiWebsocketState.CONNECTED

        status_code, headers, self.connection = self.handshake.accept(
            message.get('subprotocol'), message.get('headers', []),
        )

        await self.send(Response(stream_id=self.stream_id, status_code=status_code, headers=headers))

        log_access(
            self.config,
            self.scope,
            {
                'status': status_code,
                'headers': [],
            },
            time.time() - self.start_time,
        )

        if self.config.websocket_ping_interval is not None:
            self.task_spawner.spawn(self._send_pings)

    async def _send_rejection(self, message: WebsocketResponseBodyEvent) -> None:
        body_suppressed = suppress_body('GET', self.response['status'])

        if self.state == AsgiWebsocketState.HANDSHAKE:
            headers = build_and_validate_headers(self.response['headers'])

            await self.send(
                Response(
                    stream_id=self.stream_id,
                    status_code=int(self.response['status']),
                    headers=headers,
                ),
            )

            self.state = AsgiWebsocketState.RESPONSE

        if not body_suppressed:
            await self.send(Body(stream_id=self.stream_id, data=bytes(message.get('body', b''))))

        if not message.get('more_body', False):
            self.state = AsgiWebsocketState.HTTPCLOSED

            await self.send(EndBody(stream_id=self.stream_id))

            log_access(
                self.config,
                self.scope,
                self.response,  # type: ignore
                time.time() - self.start_time,
            )

    async def _send_pings(self) -> None:
        while not self.closed:
            await self._send_wsproto_event(wse.Ping())
            await self.context.sleep(check.not_none(self.config.websocket_ping_interval))
