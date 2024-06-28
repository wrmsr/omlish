import enum
import logging
import time
import typing as ta
import urllib.parse

from .config import Config
from .events import Body
from .events import EndBody
from .events import InformationalResponse
from .events import ProtocolEvent
from .events import Request
from .events import Response
from .events import StreamClosed
from .requests import valid_server_name
from .taskspawner import TaskSpawner
from .types import ASGISendEvent
from .types import AppWrapper
from .types import HTTPResponseStartEvent
from .types import HTTPScope
from .types import Scope
from .types import UnexpectedMessageError
from .workercontext import WorkerContext


log = logging.getLogger(__name__)


PUSH_VERSIONS = {"2", "3"}
EARLY_HINTS_VERSIONS = {"2", "3"}


class ASGIHTTPState(enum.Enum):
    # The ASGI Spec is clear that a response should not start till the
    # framework has sent at least one body message hence why this
    # state tracking is required.
    REQUEST = enum.auto()
    RESPONSE = enum.auto()
    CLOSED = enum.auto()


def build_and_validate_headers(headers: ta.Iterable[tuple[bytes, bytes]]) -> list[tuple[bytes, bytes]]:
    # Validates that the header name and value are bytes
    validated_headers: list[tuple[bytes, bytes]] = []
    for name, value in headers:
        if name[0] == b":"[0]:
            raise ValueError("Pseudo headers are not valid")
        validated_headers.append((bytes(name).strip(), bytes(value).strip()))
    return validated_headers


def suppress_body(method: str, status_code: int) -> bool:
    return method == "HEAD" or 100 <= status_code < 200 or status_code in {204, 304}


class ResponseSummary(ta.TypedDict):
    status: int
    headers: ta.Iterable[tuple[bytes, bytes]]


def log_access(
        config: Config, request: "Scope", response: ta.Optional["ResponseSummary"], request_time: float
) -> None:
    # if self.access_logger is not None:
    #     self.access_logger.info(
    #         self.access_log_format, self.atoms(request, response, request_time)
    #     )
    log.info(f'access: {request!r} {response!r}')


class HTTPStream:
    def __init__(
            self,
            app: AppWrapper,
            config: Config,
            context: WorkerContext,
            task_spawner: TaskSpawner,
            client: ta.Optional[tuple[str, int]],
            server: ta.Optional[tuple[str, int]],
            send: ta.Callable[[ProtocolEvent], ta.Awaitable[None]],
            stream_id: int,
    ) -> None:
        super().__init__()
        self.app = app
        self.client = client
        self.closed = False
        self.config = config
        self.context = context
        self.response: HTTPResponseStartEvent
        self.scope: HTTPScope
        self.send = send
        self.scheme = "http"
        self.server = server
        self.start_time: float
        self.state = ASGIHTTPState.REQUEST
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
            path, _, query_string = event.raw_path.partition(b"?")
            self.scope = {
                "type": "http",
                "http_version": event.http_version,
                "asgi": {"spec_version": "2.1", "version": "3.0"},
                "method": event.method,
                "scheme": self.scheme,
                "path": urllib.parse.unquote(path.decode("ascii")),
                "raw_path": path,
                "query_string": query_string,
                "headers": event.headers,
                "client": self.client,
                "server": self.server,
                "extensions": {},
            }
            if event.http_version in PUSH_VERSIONS:
                self.scope["extensions"]["http.response.push"] = {}

            if event.http_version in EARLY_HINTS_VERSIONS:
                self.scope["extensions"]["http.response.early_hint"] = {}

            if valid_server_name(self.config, event):
                self.app_put = await self.task_spawner.spawn_app(
                    self.app, self.config, self.scope, self.app_send
                )
            else:
                await self._send_error_response(404)
                self.closed = True

        elif isinstance(event, Body):
            await self.app_put(
                {"type": "http.request", "body": bytes(event.data), "more_body": True}
            )
        elif isinstance(event, EndBody):
            await self.app_put({"type": "http.request", "body": b"", "more_body": False})
        elif isinstance(event, StreamClosed):
            self.closed = True
            if self.state != ASGIHTTPState.CLOSED:
                log_access(self.config, self.scope, None, time.time() - self.start_time)
            if self.app_put is not None:
                await self.app_put({"type": "http.disconnect"})

    async def app_send(self, message: ta.Optional[ASGISendEvent]) -> None:
        if message is None:  # ASGI App has finished sending messages
            if not self.closed:
                # Cleanup if required
                if self.state == ASGIHTTPState.REQUEST:
                    await self._send_error_response(500)
                await self.send(StreamClosed(stream_id=self.stream_id))
        else:
            if message["type"] == "http.response.start" and self.state == ASGIHTTPState.REQUEST:
                self.response = message
            elif (
                    message["type"] == "http.response.push"
                    and self.scope["http_version"] in PUSH_VERSIONS
            ):
                if not isinstance(message["path"], str):
                    raise TypeError(f"{message['path']} should be a str")
                headers = [(b":scheme", self.scope["scheme"].encode())]
                for name, value in self.scope["headers"]:
                    if name == b"host":
                        headers.append((b":authority", value))
                headers.extend(build_and_validate_headers(message["headers"]))
                await self.send(
                    Request(
                        stream_id=self.stream_id,
                        headers=headers,
                        http_version=self.scope["http_version"],
                        method="GET",
                        raw_path=message["path"].encode(),
                    )
                )
            elif (
                    message["type"] == "http.response.early_hint"
                    and self.scope["http_version"] in EARLY_HINTS_VERSIONS
                    and self.state == ASGIHTTPState.REQUEST
            ):
                headers = [(b"link", bytes(link).strip()) for link in message["links"]]
                await self.send(
                    InformationalResponse(
                        stream_id=self.stream_id,
                        headers=headers,
                        status_code=103,
                    )
                )
            elif message["type"] == "http.response.body" and self.state in {
                ASGIHTTPState.REQUEST,
                ASGIHTTPState.RESPONSE,
            }:
                if self.state == ASGIHTTPState.REQUEST:
                    headers = build_and_validate_headers(self.response.get("headers", []))
                    await self.send(
                        Response(
                            stream_id=self.stream_id,
                            headers=headers,
                            status_code=int(self.response["status"]),
                        )
                    )
                    self.state = ASGIHTTPState.RESPONSE

                if (
                        not suppress_body(self.scope["method"], int(self.response["status"]))
                        and message.get("body", b"") != b""
                ):
                    await self.send(
                        Body(stream_id=self.stream_id, data=bytes(message.get("body", b"")))
                    )

                if not message.get("more_body", False):
                    if self.state != ASGIHTTPState.CLOSED:
                        self.state = ASGIHTTPState.CLOSED
                        log_access(
                            self.config, self.scope, self.response, time.time() - self.start_time  # type: ignore  # FIXME  # noqa
                        )
                        await self.send(EndBody(stream_id=self.stream_id))
                        await self.send(StreamClosed(stream_id=self.stream_id))
            else:
                raise UnexpectedMessageError(self.state, message["type"])

    async def _send_error_response(self, status_code: int) -> None:
        await self.send(
            Response(
                stream_id=self.stream_id,
                headers=[(b"content-length", b"0"), (b"connection", b"close")],
                status_code=status_code,
            )
        )
        await self.send(EndBody(stream_id=self.stream_id))
        self.state = ASGIHTTPState.CLOSED
        log_access(
            self.config, self.scope, {"status": status_code, "headers": []}, time.time() - self.start_time
        )
