import abc
import dataclasses as dc
import email.utils
import html
import http.client
import http.server
import time
import typing as ta

from omlish.lite.check import check_isinstance
from omlish.lite.check import check_not_none

from .logging import DefaultHttpLogging
from .logging import HttpLogging
from .parsing import EmptyParsedHttpResult
from .parsing import HttpHeaders
from .parsing import HttpProtocolVersion
from .parsing import HttpProtocolVersions
from .parsing import HttpRequestParser
from .parsing import ParsedHttpRequest
from .parsing import ParseHttpRequestError
from .sockets import SocketAddress
from .sockets import SocketRequestHandler


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


class HttpSocketRequestHandler(SocketRequestHandler):

    #

    def __init__(
            self,
            client_address: SocketAddress,
            rfile: ta.BinaryIO,
            wfile: ta.BinaryIO,
            *,
            handler: HttpServerHandler,
            parser: HttpRequestParser = HttpRequestParser(),
            logging: HttpLogging = DefaultHttpLogging(),
    ) -> None:
        super().__init__(
            client_address,
            rfile,
            wfile,
        )

        self.handler = handler
        self.parser = parser
        self.logging = logging

        self.logging_context = HttpLogging.Context(
            client=str(self.client_address[0]),
        )

        self._headers_buffer: list[bytes] = []

    #

    def format_timestamp(self, timestamp: float | None = None) -> str:
        if timestamp is None:
            timestamp = time.time()
        return email.utils.formatdate(timestamp, usegmt=True)

    #

    class Header(ta.NamedTuple):
        key: str
        value: str

    def header_encode(self, s: str) -> bytes:
        return s.encode('latin-1', 'strict')

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
            self.Header('Date', self.format_timestamp())
        ]

    #

    def format_status_line(
            self,
            code: HttpStatusOrInt,
            message: str | None = None,
    ) -> str:
        if message is None:
            if code in self._STATUS_RESPONSES:
                message = self._STATUS_RESPONSES[code][0]
            else:
                message = ''

        return f'{self.protocol_version} {int(code)} {message}\r\n'

    #

    class Action(abc.ABC):  # noqa
        pass

    @dc.dataclass(frozen=True, kw_only=True)
    class ResponseAction(Action):
        code: http.HTTPStatus
        message: str | None
        headers: ta.Sequence['HttpSocketRequestHandler.Header']
        data: bytes | None = None

    class CloseConnectionAction(Action):
        pass

    ##

    close_connection: bool

    def handle(self) -> None:
        self.close_connection = True

        self.handle_one_request()
        while not self.close_connection:
            self.handle_one_request()

    #

    protocol_version: HttpProtocolVersion
    request_line: str
    request_version: HttpProtocolVersion

    method: str | None
    path: str
    headers: HttpHeaders

    #

    def handle_one_request(self) -> ta.Iterator[Action]:
        try:
            parsed = self.parser.parse(self.rfile.readline)

            self.protocol_version = parsed.protocol_version
            self.request_line = parsed.request_line
            self.request_version = parsed.request_version
            self.close_connection = parsed.close_connection

            if isinstance(parsed, EmptyParsedHttpResult):
                # An error code has been sent, just exit
                return

            if isinstance(parsed, ParseHttpRequestError):
                self.send_error(
                    parsed.code,
                    *parsed.message,
                )
                return

            parsed = check_isinstance(parsed, ParsedHttpRequest)

            self.logging.log_message(self.logging_context, '%r', parsed)

            if parsed.expects_continue:
                # https://bugs.python.org/issue1491
                # https://github.com/python/cpython/commit/0f476d49f8d4aa84210392bf13b59afc67b32b31
                self.send_status_line(http.HTTPStatus.CONTINUE)
                self.end_headers()

            self.method = parsed.method
            self.path = parsed.path
            self.headers = parsed.headers

            request_data: bytes | None
            if (cl := self.headers.get('Content-Length')) is not None:
                request_data = self.rfile.read(int(cl))
            else:
                request_data = None

            request = HttpServerRequest(
                client_address=self.client_address,
                method=check_not_none(self.method),
                path=self.path,
                headers=self.headers,
                data=request_data,
            )

            try:
                response = self.handler(request)
            except UnsupportedMethodServerHandlerError:
                self.send_error(
                    http.HTTPStatus.NOT_IMPLEMENTED,
                    f'Unsupported method ({self.method!r})',
                )
                self.wfile.flush()  # actually send the response if not already done.
                return

            if response.close_connection is not None:
                self.close_connection = response.close_connection
            response_headers = response.headers or {}
            response_data = response.data

            self.send_response(response.status)

            for k, v in response_headers.items():
                self.send_header(k, v)
            if 'Content-Type' not in response_headers:
                self.send_header('Content-Type', 'text/plain')
            if 'Content-Length' not in response_headers and response_data is not None:
                self.send_header('Content-Length', str(len(response_data)))
            self.end_headers()

            if response_data is not None:
                self.wfile.write(response_data)

            self.wfile.flush()  # actually send the response if not already done.

        except TimeoutError as e:
            # A read or a write timed out. Discard this connection
            self.logging.log_error(self.logging_context, 'Request timed out: %r', e)
            self.close_connection = True
            return

    #

    _STATUS_RESPONSES: ta.Mapping[int, tuple[str, str]] = {
        v: (v.phrase, v.description)
        for v in http.HTTPStatus.__members__.values()
    }

    DEFAULT_ERROR_MESSAGE = """\
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
    """

    DEFAULT_ERROR_CONTENT_TYPE = 'text/html;charset=utf-8'

    error_message_format = DEFAULT_ERROR_MESSAGE
    error_content_type = DEFAULT_ERROR_CONTENT_TYPE

    def send_error(
            self,
            code: HttpStatusOrInt,
            message: str | None = None,
            explain: str | None = None,
    ) -> ta.Iterator[Action]:
        headers: list[HttpSocketRequestHandler.Header] = [
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

        self.logging.log_error(self.logging_context, 'code %d, message %s', code, message)

        headers.append(self.Header('Connection', 'close'))

        # Message body is omitted for cases described in:
        #  - RFC7230: 3.3. 1xx, 204(No Content), 304(Not Modified)
        #  - RFC7231: 6.3.6. 205(Reset Content)
        body: bytes | None = None
        if (
                code >= 200 and
                code not in (
                    http.HTTPStatus.NO_CONTENT,
                    http.HTTPStatus.RESET_CONTENT,
                    http.HTTPStatus.NOT_MODIFIED,
                )
        ):
            # HTML encode to prevent Cross Site Scripting attacks (see bug #1100201)
            content = (self.error_message_format % {
                'code': code,
                'message': html.escape(message, quote=False),
                'explain': html.escape(explain, quote=False),
            })
            body = content.encode('UTF-8', 'replace')

            headers.extend([
                self.Header('Content-Type', self.error_content_type),
                self.Header('Content-Length', str(len(body))),
            ])

        self.end_headers()

        if self.method != 'HEAD' and body:
            self.wfile.write(body)
