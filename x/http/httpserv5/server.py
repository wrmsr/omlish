"""
"Test suite" lol:

curl -v localhost:8000
curl -v localhost:8000 -d 'foo'

curl -v -XPOST -H 'Expect: 100-Continue' localhost:8000 -d 'foo'

curl -v -XFOO localhost:8000 -d 'foo'

curl -v -XPOST localhost:8000 -d 'foo' --next -XPOST localhost:8000 -d 'bar'
curl -v -XPOST localhost:8000 -d 'foo' --next -XFOO localhost:8000 -d 'bar'
curl -v -XFOO localhost:8000 -d 'foo' --next -XPOST localhost:8000 -d 'bar'
curl -v -XFOO localhost:8000 -d 'foo' --next -XFOO localhost:8000 -d 'bar'
"""
import abc
import dataclasses as dc
import email.utils
import html
import http.client
import http.server
import io
import textwrap
import time
import typing as ta

from omlish.lite.check import check_isinstance
from omlish.lite.check import check_not_none
from omlish.lite.http.parsing import EmptyParsedHttpResult
from omlish.lite.http.parsing import HttpHeaders
from omlish.lite.http.parsing import HttpRequestParser
from omlish.lite.http.parsing import ParseHttpRequestError
from omlish.lite.http.parsing import ParsedHttpRequest
from omlish.lite.http.versions import HttpProtocolVersion
from omlish.lite.http.versions import HttpProtocolVersions

from .logging import DefaultHttpLogging
from .logging import HttpLogging
from .sockets import SocketAddress
from .sockets import SocketHandler


HttpStatusOrInt: ta.TypeAlias = http.HTTPStatus | int


##


@dc.dataclass(frozen=True)
class HttpServerRequest:
    client_address: SocketAddress
    method: str
    path: str
    headers: HttpHeaders
    data: bytes | None


@dc.dataclass(frozen=True)
class HttpServerResponse:
    status: HttpStatusOrInt
    _: dc.KW_ONLY
    headers: ta.Mapping[str, str] | None = None
    data: bytes | None = None
    close_connection: bool | None = None


class HttpServerHandlerError(Exception):
    pass


class UnsupportedMethodServerHandlerError(Exception):
    pass


HttpServerHandler: ta.TypeAlias = ta.Callable[[HttpServerRequest], HttpServerResponse]


##


class HttpServer:

    #

    def __init__(
            self,
            client_address: SocketAddress,
            *,
            handler: HttpServerHandler,
            parser: HttpRequestParser = HttpRequestParser(),
            logging: HttpLogging = DefaultHttpLogging(),

            default_content_type: str | None = None,

            error_message_format: str | None = None,
            error_content_type: str | None = None,
    ) -> None:
        super().__init__()

        self._client_address = client_address

        self._handler = handler
        self._parser = parser
        self._logging = logging

        self._logging_context = HttpLogging.Context(
            client=str(self._client_address[0]),
        )

        self._default_content_type = default_content_type or self.DEFAULT_CONTENT_TYPE

        self._error_message_format = error_message_format or self.DEFAULT_ERROR_MESSAGE
        self._error_content_type = error_content_type or self.DEFAULT_ERROR_CONTENT_TYPE

    #

    def format_timestamp(self, timestamp: float | None = None) -> str:
        if timestamp is None:
            timestamp = time.time()
        return email.utils.formatdate(timestamp, usegmt=True)

    #

    def header_encode(self, s: str) -> bytes:
        return s.encode('latin-1', 'strict')

    class Header(ta.NamedTuple):
        key: str
        value: str

    def format_header_line(self, h: Header) -> str:
        return f'{h.key}: {h.value}\r\n'

    def get_header_close_connection_action(self, h: Header) -> bool | None:
        if h.key.lower() != 'connection':
            return None
        elif h.value.lower() == 'close':
            return True
        elif h.value.lower() == 'keep-alive':
            return False
        else:
            return None

    def make_default_headers(self) -> list[Header]:
        return [
            self.Header('Date', self.format_timestamp()),
        ]

    #

    _STATUS_RESPONSES: ta.Mapping[int, tuple[str, str]] = {
        v: (v.phrase, v.description)
        for v in http.HTTPStatus.__members__.values()
    }

    def format_status_line(
            self,
            version: HttpProtocolVersion,
            code: HttpStatusOrInt,
            message: str | None = None,
    ) -> str:
        if message is None:
            if code in self._STATUS_RESPONSES:
                message = self._STATUS_RESPONSES[code][0]
            else:
                message = ''

        return f'{version} {int(code)} {message}\r\n'

    #

    @dc.dataclass(frozen=True, kw_only=True)
    class Response:
        version: HttpProtocolVersion
        code: http.HTTPStatus
        message: str | None = None
        headers: ta.Sequence['HttpServer.Header'] | None = None
        data: bytes | None = None
        close_connection: bool = False

        def get_header(self, key: str) -> ta.Optional['HttpServer.Header']:
            for h in self.headers or []:
                if h.key.lower() == key.lower():
                    return h
            return None

    #

    def build_response_bytes(self, a: Response) -> bytes:
        out = io.BytesIO()

        if a.version >= HttpProtocolVersions.HTTP_1_0:
            out.write(self.header_encode(self.format_status_line(
                a.version,
                a.code,
                a.message,
            )))

            for h in a.headers or []:
                out.write(self.header_encode(self.format_header_line(h)))

            out.write(b'\r\n')

        if a.data is not None:
            out.write(a.data)

        return out.getvalue()

    #

    DEFAULT_CONTENT_TYPE = 'text/plain'

    def preprocess_response(self, a: Response) -> Response:
        nh: list[HttpServer.Header] = []
        kw: dict[str, ta.Any] = {}

        if a.get_header('Content-Type') is None:
            nh.append(self.Header('Content-Type', self._default_content_type))
        if a.data is not None and a.get_header('Content-Length') is None:
            nh.append(self.Header('Content-Length', str(len(a.data))))

        if nh:
            kw.update(headers=[*(a.headers or []), *nh])

        if (clh := a.get_header('Connection')) is not None:
            if self.get_header_close_connection_action(clh):
                kw.update(close_connection=True)

        if not kw:
            return a
        return dc.replace(a, **kw)

    def preprocess_actions(self, actions: ta.Sequence[Action]) -> ta.Iterator[Action]:
        for a in actions:
            if isinstance(a, self.ResponseAction):
                yield self.preprocess_response(a)

                if (clh := a.get_header('Connection')) is not None:
                    if self.get_header_close_connection_action(clh):
                        yield self.CloseConnectionAction()
                        break

            elif isinstance(a, self.CloseConnectionAction):
                yield a
                break

            else:
                raise TypeError(a)

    #

    class Io(abc.ABC):  # noqa
        pass

    @dc.dataclass(frozen=True)
    class ReadIo(Io):
        sz: int
        line: bool

    @dc.dataclass(frozen=True)
    class WriteIo(Io):
        data: bytes

    #

    def coro_handle(self) -> ta.Generator[Io, bytes | None, None]:
        while True:
            gen = self.coro_handle_one()
            o = next(gen)
            i: bytes | None
            while True:
                if isinstance(o, self.Io):
                    i = yield o

                elif isinstance(o, self.Action):
                    i = None
                    for a in self.preprocess_actions(actions):
                        print(a)
                        if isinstance(a, self.ResponseAction):
                            out = self.build_response_bytes(a)
                            yield self.WriteIo(out)

                        elif isinstance(a, self.CloseConnectionAction):
                            return

                        else:
                            raise TypeError(a)

    def coro_handle_one(self) -> ta.Generator[Io | Action, bytes | None, None]:
        gen = self._parser.coro_parse()
        sz = next(gen)
        while True:
            try:
                line = yield self.ReadIo(sz, True)
                sz = gen.send(line)
            except StopIteration as e:
                parsed = e.value
                break

        if isinstance(parsed, EmptyParsedHttpResult):
            yield self.CloseConnectionAction()
            return

        if isinstance(parsed, ParseHttpRequestError):
            yield from self.send_error(
                parsed.code,
                *parsed.message,
                version=parsed.version,
            )
            return

        parsed = check_isinstance(parsed, ParsedHttpRequest)

        self._logging.log_message(self._logging_context, '%r', parsed)

        if parsed.expects_continue:
            # https://bugs.python.org/issue1491
            # https://github.com/python/cpython/commit/0f476d49f8d4aa84210392bf13b59afc67b32b31
            yield self.ResponseAction(
                version=parsed.version,
                code=http.HTTPStatus.CONTINUE,
            )

        yield from self.coro_send_handled(parsed)

    #

    def coro_send_handled(
            self,
            parsed: ParsedHttpRequest,
    ) -> ta.Generator[Io | Action, bytes | None, None]:
        # Read data

        request_data: bytes | None
        if (cl := parsed.headers.get('Content-Length')) is not None:
            request_data = yield self.ReadIo(int(cl), False)
        else:
            request_data = None

        # Build request

        request = HttpServerRequest(
            client_address=self._client_address,
            method=check_not_none(parsed.method),
            path=parsed.path,
            headers=parsed.headers,
            data=request_data,
        )

        # Build response

        try:
            response = self._handler(request)
        except UnsupportedMethodServerHandlerError:
            yield from self.send_error(
                http.HTTPStatus.NOT_IMPLEMENTED,
                f'Unsupported method ({parsed.method!r})',
                version=parsed.version,
                method=parsed.method,
            )
            return

        # Build action

        response_headers = response.headers or {}
        response_data = response.data

        headers: list[HttpServer.Header] = [
            *self.make_default_headers(),
        ]

        for k, v in response_headers.items():
            headers.append(self.Header(k, v))

        if response.close_connection and 'Connection' not in headers:
            headers.append(self.Header('Connection', 'close'))

        action = self.ResponseAction(
            version=parsed.version,
            code=http.HTTPStatus(response.status),
            headers=headers,
            data=response_data,
        )

        # Emit actions

        yield action

        if response.close_connection:
            yield self.CloseConnectionAction()

    #

    DEFAULT_ERROR_MESSAGE = textwrap.dedent("""\
        <!DOCTYPE HTML>
        <html lang="en">
            <head>
                <meta charset="utf-8">
                <title>Error response</title>
            </head>
            <body>
                <h1>Error response</h1>
                <p>Error code: %(code)d</p>
                <p>Message: %(message)s.</p>
                <p>Error code explanation: %(code)s - %(explain)s.</p>
            </body>
        </html>
    """)

    DEFAULT_ERROR_CONTENT_TYPE = 'text/html;charset=utf-8'

    def build_error_response(
            self,
            code: HttpStatusOrInt,
            message: str | None = None,
            explain: str | None = None,
            *,
            version: HttpProtocolVersion | None = None,
            method: str | None = None,
    ) -> ResponseAction:
        code = http.HTTPStatus(code)

        headers: list[HttpServer.Header] = [
            *self.make_default_headers(),
        ]

        try:
            short_msg, long_msg = self._STATUS_RESPONSES[code]
        except KeyError:
            short_msg, long_msg = '???', '???'
        if message is None:
            message = short_msg
        if explain is None:
            explain = long_msg

        self._logging.log_error(self._logging_context, 'code %d, message %s', code, message)

        headers.append(self.Header('Connection', 'close'))

        # Message body is omitted for cases described in:
        #  - RFC7230: 3.3. 1xx, 204(No Content), 304(Not Modified)
        #  - RFC7231: 6.3.6. 205(Reset Content)
        data: bytes | None = None
        if (
                code >= http.HTTPStatus.OK and
                code not in (
                    http.HTTPStatus.NO_CONTENT,
                    http.HTTPStatus.RESET_CONTENT,
                    http.HTTPStatus.NOT_MODIFIED,
                )
        ):
            # HTML encode to prevent Cross Site Scripting attacks (see bug #1100201)
            content = self._error_message_format.format(
                code=code,
                message=html.escape(message, quote=False),
                explain=html.escape(explain, quote=False),
            )
            body = content.encode('UTF-8', 'replace')

            headers.extend([
                self.Header('Content-Type', self._error_content_type),
                self.Header('Content-Length', str(len(body))),
            ])

            if method != 'HEAD' and body:
                data = body

        return self.ResponseAction(
            version=version or self._parser.server_version,
            code=code,
            message=message,
            headers=headers,
            data=data,
            close_connection=True,
        )
