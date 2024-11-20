import abc
import dataclasses as dc
import email.utils
import html
import http.client
import http.server
import io
import time
import typing as ta

from omlish import check

from .logging import DefaultHttpLogging
from .logging import HttpLogging
from .sockets import SocketAddress
from .sockets import SocketRequestHandler


HttpStatusOrInt: ta.TypeAlias = http.HTTPStatus | int


##


@dc.dataclass(frozen=True)
class HttpServerRequest:
    client_address: SocketAddress
    method: str
    path: str
    headers: http.client.HTTPMessage
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
            logging: HttpLogging = DefaultHttpLogging(),
    ) -> None:
        super().__init__(
            client_address,
            rfile,
            wfile,
        )

        self.handler = handler
        self.logging = logging

        self.logging_context = HttpLogging.Context(
            client=str(self.client_address[0]),
        )

    #

    DEFAULT_PROTOCOL_VERSION = 'HTTP/1.0'

    protocol_version = DEFAULT_PROTOCOL_VERSION

    #

    close_connection: bool

    def handle(self) -> None:
        self.close_connection = True

        self.handle_one_request()
        while not self.close_connection:
            self.handle_one_request()

    #

    raw_request_line: bytes

    request_version: str
    request_line: str
    method: str | None

    def handle_one_request(self) -> None:
        try:
            self.raw_request_line = self.rfile.readline(65537)

            if len(self.raw_request_line) > 65536:
                self.request_line = ''
                self.request_version = ''
                self.method = ''
                self.send_error(http.HTTPStatus.REQUEST_URI_TOO_LONG)
                return

            if not self.raw_request_line:
                self.close_connection = True
                return

            if not self.parse_request():
                # An error code has been sent, just exit
                return

            self.invoke_handler()

            self.wfile.flush()  # actually send the response if not already done.

        except TimeoutError as e:
            # A read or a write timed out. Discard this connection
            self.logging.log_error(self.logging_context, 'Request timed out: %r', e)
            self.close_connection = True
            return
    #

    def invoke_handler(self) -> None:
        request_data: bytes | None
        if (cl := self.headers.get('Content-Length')) is not None:
            request_data = self.rfile.read(int(cl))
        else:
            request_data = None

        request = HttpServerRequest(
            client_address=self.client_address,
            method=check.not_none(self.method),
            path=self.path,
            headers=self.headers,
            data=request_data,
        )

        try:
            response = self.handler(request)
        except UnsupportedMethodServerHandlerError:
            # FIXME: close_connection?
            self.send_error(
                http.HTTPStatus.NOT_IMPLEMENTED,
                f'Unsupported method ({self.method!r})',
            )
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

    #


    path: str

    headers: http.client.HTTPMessage

    class ParsedRequest(ta.NamedTuple):
        pass

    class ParseRequestError(ta.NamedTuple):
        code: http.HTTPStatus
        message: str

    def parse_request(self) -> bool:
        self.method = None  # set in case of error on the first line
        self.request_version = self.default_request_version
        self.close_connection = True

        request_line = self.raw_request_line.decode('iso-8859-1')
        request_line = request_line.rstrip('\r\n')
        self.request_line = request_line

        words = request_line.split()
        if len(words) == 0:
            return False

        if len(words) >= 3:  # Enough to determine protocol version
            version = words[-1]
            try:
                if not version.startswith('HTTP/'):
                    raise ValueError(version)  # noqa

                base_version_number = version.split('/', 1)[1]
                version_number_parts = base_version_number.split('.')

                # RFC 2145 section 3.1 says there can be only one "." and
                #   - major and minor numbers MUST be treated as separate integers;
                #   - HTTP/2.4 is a lower version than HTTP/2.13, which in turn is lower than HTTP/12.3;
                #   - Leading zeros MUST be ignored by recipients.
                if len(version_number_parts) != 2:
                    raise ValueError(version_number_parts)  # noqa
                if any(not component.isdigit() for component in version_number_parts):
                    raise ValueError('non digit in http version')  # noqa
                if any(len(component) > 10 for component in version_number_parts):
                    raise ValueError('unreasonable length http version')  # noqa
                version_number = int(version_number_parts[0]), int(version_number_parts[1])

            except (ValueError, IndexError):
                self.send_error(
                    http.HTTPStatus.BAD_REQUEST,
                    f'Bad request version ({version!r})',
                )
                return False

            if version_number >= (1, 1) and self.protocol_version >= 'HTTP/1.1':
                self.close_connection = False

            if version_number >= (2, 0):
                self.send_error(
                    http.HTTPStatus.HTTP_VERSION_NOT_SUPPORTED,
                    f'Invalid HTTP version ({base_version_number})',
                )
                return False

            self.request_version = version

        if not 2 <= len(words) <= 3:
            self.send_error(
                http.HTTPStatus.BAD_REQUEST,
                f'Bad request syntax ({request_line!r})',
            )
            return False

        method, path = words[:2]
        if len(words) == 2:
            self.close_connection = True
            if method != 'GET':
                self.send_error(
                    http.HTTPStatus.BAD_REQUEST,
                    f'Bad HTTP/0.9 request type ({method!r})',
                )
                return False

        self.method = method
        self.path = path

        # gh-87389: The purpose of replacing '//' with '/' is to protect against open redirect attacks possibly
        # triggered if the path starts with '//' because http clients treat //path as an absolute URI without scheme
        # (similar to http://path) rather than a path.
        if self.path.startswith('//'):
            self.path = '/' + self.path.lstrip('/')  # Reduce to a single /

        # Examine the headers and look for a Connection directive.
        try:
            raw_headers = read_raw_http_headers(self.rfile)
            self.headers = parse_raw_http_headers(raw_headers)

        except http.client.LineTooLong as err:
            self.send_error(
                http.HTTPStatus.REQUEST_HEADER_FIELDS_TOO_LARGE,
                'Line too long',
                str(err),
            )
            return False

        except http.client.HTTPException as err:
            self.send_error(
                http.HTTPStatus.REQUEST_HEADER_FIELDS_TOO_LARGE,
                'Too many headers',
                str(err),
            )
            return False

        conn_type = self.headers.get('Connection', '')
        if conn_type.lower() == 'close':
            self.close_connection = True
        elif (
                conn_type.lower() == 'keep-alive' and
                self.protocol_version >= 'HTTP/1.1'
        ):
            self.close_connection = False

        # Examine the headers and look for an Expect directive
        expect = self.headers.get('Expect', '')
        if (
                expect.lower() == '100-continue' and
                self.protocol_version >= 'HTTP/1.1' and
                self.request_version >= 'HTTP/1.1'
        ):
            if not self.handle_expect_100():
                return False

        return True

    #

    def handle_expect_100(self) -> bool:
        self.send_response_only(http.HTTPStatus.CONTINUE)
        self.end_headers()
        return True

    #

    _STATUS_RESPONSES: ta.Mapping[int, tuple[str, str]] = {
        v: (v.phrase, v.description)
        for v in http.HTTPStatus.__members__.values()
    }

    error_message_format = DEFAULT_ERROR_MESSAGE
    error_content_type = DEFAULT_ERROR_CONTENT_TYPE

    def send_error(
            self,
            code: HttpStatusOrInt,
            message: str | None = None,
            explain: str | None = None,
    ) -> None:
        try:
            short_msg, long_msg = self._STATUS_RESPONSES[code]
        except KeyError:
            short_msg, long_msg = '???', '???'
        if message is None:
            message = short_msg
        if explain is None:
            explain = long_msg

        self.logging.log_error(self.logging_context, 'code %d, message %s', code, message)

        self.send_response(code, message)
        self.send_header('Connection', 'close')

        # Message body is omitted for cases described in:
        #  - RFC7230: 3.3. 1xx, 204(No Content), 304(Not Modified)
        #  - RFC7231: 6.3.6. 205(Reset Content)
        body = None
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
            self.send_header('Content-Type', self.error_content_type)
            self.send_header('Content-Length', str(len(body)))

        self.end_headers()

        if self.method != 'HEAD' and body:
            self.wfile.write(body)

    #

    _headers_buffer: list[bytes]

    def send_header(self, keyword: str, value: str) -> None:
        if self.request_version != 'HTTP/0.9':
            if not hasattr(self, '_headers_buffer'):
                self._headers_buffer = []
            line = f'{keyword}: {value}\r\n'
            self._headers_buffer.append(line.encode('latin-1', 'strict'))

        if keyword.lower() == 'connection':
            if value.lower() == 'close':
                self.close_connection = True
            elif value.lower() == 'keep-alive':
                self.close_connection = False

    def end_headers(self) -> None:
        if self.request_version != 'HTTP/0.9':
            self._headers_buffer.append(b'\r\n')
            self.flush_headers()

    def flush_headers(self) -> None:
        if hasattr(self, '_headers_buffer'):
            self.wfile.write(b''.join(self._headers_buffer))
            self._headers_buffer = []

    #

    def format_timestamp(self, timestamp: float | None = None) -> str:
        if timestamp is None:
            timestamp = time.time()
        return email.utils.formatdate(timestamp, usegmt=True)

    #

    def send_response(self, code: HttpStatusOrInt, message: str | None = None) -> None:
        self.logging.log_request(self.logging_context, self.request_line, code)
        self.send_response_only(code, message)
        self.send_header('Date', self.format_timestamp())

    def send_response_only(self, code: HttpStatusOrInt, message: str | None = None) -> None:
        if self.request_version != 'HTTP/0.9':
            if message is None:
                if code in self._STATUS_RESPONSES:
                    message = self._STATUS_RESPONSES[code][0]
                else:
                    message = ''

            if not hasattr(self, '_headers_buffer'):
                self._headers_buffer = []

            line = f'{self.protocol_version} {int(code)} {message}\r\n'
            self._headers_buffer.append(line.encode('latin-1', 'strict'))
