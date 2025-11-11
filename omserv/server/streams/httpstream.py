import enum
import time
import typing as ta
import urllib.parse

from omlish.logs import all as logs

from ..config import Config
from ..events import Body
from ..events import EndBody
from ..events import InformationalResponse
from ..events import ProtocolEvent
from ..events import Request
from ..events import Response
from ..events import StreamClosed
from ..events import Trailers
from ..taskspawner import TaskSpawner
from ..types import AppWrapper
from ..types import AsgiSendEvent
from ..types import HttpResponseStartEvent
from ..types import HttpScope
from ..types import UnexpectedMessageError
from ..workercontext import WorkerContext
from .utils import build_and_validate_headers
from .utils import log_access
from .utils import suppress_body
from .utils import valid_server_name


log = logs.get_module_logger(globals())


##


TRAILERS_VERSIONS = {'2', '3'}
PUSH_VERSIONS = {'2', '3'}
EARLY_HINTS_VERSIONS = {'2', '3'}


class AsgiHttpState(enum.Enum):
    # The Asgi Spec is clear that a response should not start till the framework has sent at least one body message
    # hence why this state tracking is required.
    REQUEST = enum.auto()
    RESPONSE = enum.auto()
    TRAILERS = enum.auto()
    CLOSED = enum.auto()


class HttpStream:
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
        self.client = client
        self.closed = False
        self.config = config
        self.context = context
        self.response: HttpResponseStartEvent
        self.scope: HttpScope
        self.send = send
        self.scheme = 'http'
        self.server = server
        self.start_time: float
        self.state = AsgiHttpState.REQUEST
        self.stream_id = stream_id
        self.task_spawner = task_spawner

    @property
    def idle(self) -> bool:
        return False

    async def handle(self, event: ProtocolEvent) -> None:
        if self.closed:
            return

        elif isinstance(event, Request):
            self.start_time = time.time()

            path, _, query_string = event.raw_path.partition(b'?')

            self.scope = {
                'type': 'http',
                'http_version': event.http_version,
                'asgi': {'spec_version': '2.1', 'version': '3.0'},
                'method': event.method,
                'scheme': self.scheme,
                'path': urllib.parse.unquote(path.decode('ascii')),
                'raw_path': path,
                'query_string': query_string,
                'headers': event.headers,
                'client': self.client,
                'server': self.server,
                'extensions': {},
            }

            if event.http_version in TRAILERS_VERSIONS:
                self.scope['extensions']['http.response.trailers'] = {}

            if event.http_version in PUSH_VERSIONS:
                self.scope['extensions']['http.response.push'] = {}

            if event.http_version in EARLY_HINTS_VERSIONS:
                self.scope['extensions']['http.response.early_hint'] = {}

            if valid_server_name(self.config, event):
                self.app_put = await self.task_spawner.spawn_app(self.app, self.config, self.scope, self.app_send)

            else:
                await self._send_error_response(404)
                self.closed = True

        elif isinstance(event, Body):
            await self.app_put({'type': 'http.request', 'body': bytes(event.data), 'more_body': True})

        elif isinstance(event, EndBody):
            await self.app_put({'type': 'http.request', 'body': b'', 'more_body': False})

        elif isinstance(event, StreamClosed):
            self.closed = True

            if self.state != AsgiHttpState.CLOSED:
                log_access(self.config, self.scope, None, time.time() - self.start_time)

            if self.app_put is not None:
                await self.app_put({'type': 'http.disconnect'})

    async def app_send(self, message: AsgiSendEvent | None) -> None:
        if message is None:  # Asgi App has finished sending messages
            if not self.closed:
                # Cleanup if required
                if self.state == AsgiHttpState.REQUEST:
                    await self._send_error_response(500)

                await self.send(StreamClosed(stream_id=self.stream_id))

        elif message['type'] == 'http.response.start' and self.state == AsgiHttpState.REQUEST:
            self.response = message

        elif (
                message['type'] == 'http.response.push' and
                self.scope['http_version'] in PUSH_VERSIONS
        ):
            if not isinstance(message['path'], str):
                raise TypeError(f'{message["path"]} should be a str')

            headers = [(b':scheme', self.scope['scheme'].encode())]
            for name, value in self.scope['headers']:
                if name == b'host':
                    headers.append((b':authority', value))

            headers.extend(build_and_validate_headers(message['headers']))

            await self.send(Request(
                stream_id=self.stream_id,
                headers=headers,
                http_version=self.scope['http_version'],
                method='GET',
                raw_path=message['path'].encode(),
            ))

        elif (
                message['type'] == 'http.response.early_hint'
                and self.scope['http_version'] in EARLY_HINTS_VERSIONS
                and self.state == AsgiHttpState.REQUEST
        ):
            headers = [(b'link', bytes(link).strip()) for link in message['links']]

            await self.send(
                InformationalResponse(
                    stream_id=self.stream_id,
                    headers=headers,
                    status_code=103,
                ),
            )

        elif message['type'] == 'http.response.body' and self.state in {
            AsgiHttpState.REQUEST,
            AsgiHttpState.RESPONSE,
        }:
            if self.state == AsgiHttpState.REQUEST:
                headers = build_and_validate_headers(self.response.get('headers', []))

                await self.send(Response(
                    stream_id=self.stream_id,
                    headers=headers,
                    status_code=int(self.response['status']),
                ))

                self.state = AsgiHttpState.RESPONSE

            if (
                    not suppress_body(self.scope['method'], int(self.response['status']))
                    and message.get('body', b'') != b''
            ):
                await self.send(Body(stream_id=self.stream_id, data=bytes(message.get('body', b''))))

            if not message.get('more_body', False):
                await self.send(EndBody(stream_id=self.stream_id))

                if self.response.get('trailers', False):
                    self.state = AsgiHttpState.TRAILERS

                else:
                    self.state = AsgiHttpState.CLOSED

                    log_access(
                        self.config,
                        self.scope,
                        self.response,  # type: ignore  # FIXME  # noqa
                        time.time() - self.start_time,
                    )

                    await self.send(StreamClosed(stream_id=self.stream_id))

            elif (
                    message['type'] == 'http.response.trailers' and
                    self.scope['http_version'] in TRAILERS_VERSIONS and
                    self.state == AsgiHttpState.TRAILERS
            ):
                for name, value in self.scope['headers']:
                    if name == b'te' and value == b'trailers':
                        headers = build_and_validate_headers(message['headers'])

                        await self.send(Trailers(stream_id=self.stream_id, headers=headers))

                        break

                if not message.get('more_trailers', False):
                    self.state = AsgiHttpState.CLOSED

                    log_access(
                        self.config,
                        self.scope,
                        self.response,  # type: ignore  # noqa
                        time.time() - self.start_time,
                    )

                    await self.send(StreamClosed(stream_id=self.stream_id))

            else:
                raise UnexpectedMessageError(self.state, message['type'])

    async def _send_error_response(self, status_code: int) -> None:
        await self.send(Response(
            stream_id=self.stream_id,
            headers=[
                (b'content-length', b'0'),
                (b'connection', b'close'),
            ],
            status_code=status_code,
        ))

        await self.send(EndBody(stream_id=self.stream_id))

        self.state = AsgiHttpState.CLOSED

        log_access(
            self.config,
            self.scope,
            {
                'status': status_code,
                'headers': [],
            },
            time.time() - self.start_time,
        )
