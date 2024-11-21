"""
"Test suite" lol:

curl -v localhost:8000
curl -v localhost:8000 -d 'foo'
curl -v -XFOO localhost:8000 -d 'foo'
curl -v -XPOST -H 'Expect: 100-Continue' localhost:8000 -d 'foo'

curl -v -0 localhost:8000
curl -v -0 localhost:8000 -d 'foo'
curl -v -0 -XFOO localhost:8000 -d 'foo'

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
from omlish.lite.check import check_none
from omlish.lite.check import check_not_none
from omlish.lite.http.handlers import HttpHandler
from omlish.lite.http.handlers import HttpHandlerRequest
from omlish.lite.http.handlers import UnsupportedMethodHttpHandlerError
from omlish.lite.http.parsing import EmptyParsedHttpResult
from omlish.lite.http.parsing import HttpRequestParser
from omlish.lite.http.parsing import ParseHttpRequestError
from omlish.lite.http.parsing import ParsedHttpRequest
from omlish.lite.http.versions import HttpProtocolVersion
from omlish.lite.http.versions import HttpProtocolVersions
from omlish.lite.socket import SocketAddress
from omlish.lite.socket import SocketHandler

from .logging import DefaultHttpLogging
from .logging import HttpLogging


##

##


CoroHttpServerFactory = ta.Callable[[SocketAddress], 'CoroHttpServer']


class CoroHttpServer:

    #

    def __init__(
            self,
            client_address: SocketAddress,
            *,
            handler: HttpHandler,
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

    def _format_timestamp(self, timestamp: float | None = None) -> str:
        if timestamp is None:
            timestamp = time.time()
        return email.utils.formatdate(timestamp, usegmt=True)

    #

    def _header_encode(self, s: str) -> bytes:
        return s.encode('latin-1', 'strict')

    class _Header(ta.NamedTuple):
        key: str
        value: str

    def _format_header_line(self, h: _Header) -> str:
        return f'{h.key}: {h.value}\r\n'

    def _get_header_close_connection_action(self, h: _Header) -> bool | None:
        if h.key.lower() != 'connection':
            return None
        elif h.value.lower() == 'close':
            return True
        elif h.value.lower() == 'keep-alive':
            return False
        else:
            return None

    def _make_default_headers(self) -> list[_Header]:
        return [
            self._Header('Date', self._format_timestamp()),
        ]

    #

    _STATUS_RESPONSES: ta.Mapping[int, tuple[str, str]] = {
        v: (v.phrase, v.description)
        for v in http.HTTPStatus.__members__.values()
    }

    def _format_status_line(
            self,
            version: HttpProtocolVersion,
            code: ta.Union[http.HTTPStatus, int],
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
    class _InternalResponse:
        version: HttpProtocolVersion
        code: http.HTTPStatus
        message: str | None = None
        headers: ta.Sequence['CoroHttpServer._Header'] | None = None
        data: bytes | None = None
        close_connection: bool = False

        def get_header(self, key: str) -> ta.Optional['CoroHttpServer._Header']:
            for h in self.headers or []:
                if h.key.lower() == key.lower():
                    return h
            return None

    #

    def _build_internal_response_bytes(self, a: _InternalResponse) -> bytes:
        out = io.BytesIO()

        if a.version >= HttpProtocolVersions.HTTP_1_0:
            out.write(self._header_encode(self._format_status_line(
                a.version,
                a.code,
                a.message,
            )))

            for h in a.headers or []:
                out.write(self._header_encode(self._format_header_line(h)))

            out.write(b'\r\n')

        if a.data is not None:
            out.write(a.data)

        return out.getvalue()

    #

    DEFAULT_CONTENT_TYPE = 'text/plain'

    def _preprocess_internal_response(self, resp: _InternalResponse) -> _InternalResponse:
        nh: list[CoroHttpServer._Header] = []
        kw: dict[str, ta.Any] = {}

        if resp.get_header('Content-Type') is None:
            nh.append(self._Header('Content-Type', self._default_content_type))
        if resp.data is not None and resp.get_header('Content-Length') is None:
            nh.append(self._Header('Content-Length', str(len(resp.data))))

        if nh:
            kw.update(headers=[*(resp.headers or []), *nh])

        if (clh := resp.get_header('Connection')) is not None:
            if self._get_header_close_connection_action(clh):
                kw.update(close_connection=True)

        if not kw:
            return resp
        return dc.replace(resp, **kw)

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

    def _build_error_internal_response(
            self,
            code: ta.Union[http.HTTPStatus, int],
            message: str | None = None,
            explain: str | None = None,
            *,
            version: HttpProtocolVersion | None = None,
            method: str | None = None,
    ) -> _InternalResponse:
        code = http.HTTPStatus(code)

        headers: list[CoroHttpServer._Header] = [
            *self._make_default_headers(),
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

        headers.append(self._Header('Connection', 'close'))

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
                self._Header('Content-Type', self._error_content_type),
                self._Header('Content-Length', str(len(body))),
            ])

            if method != 'HEAD' and body:
                data = body

        return self._InternalResponse(
            version=version or self._parser.server_version,
            code=code,
            message=message,
            headers=headers,
            data=data,
            close_connection=True,
        )

    #

    class Io(abc.ABC):  # noqa
        pass

    class AnyReadIo(Io):  # noqa
        pass

    @dc.dataclass(frozen=True)
    class ReadIo(AnyReadIo):
        sz: int

    @dc.dataclass(frozen=True)
    class ReadLineIo(AnyReadIo):
        sz: int

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
                if isinstance(o, self.AnyReadIo):
                    i = check_isinstance((yield o), bytes)

                elif isinstance(o, self._InternalResponse):
                    i = None
                    r = self._preprocess_internal_response(o)
                    b = self._build_internal_response_bytes(r)
                    check_none((yield self.WriteIo(b)))

                else:
                    raise TypeError(o)

                try:
                    o = gen.send(i)
                except EOFError:
                    return
                except StopIteration:
                    break

    def coro_handle_one(self) -> ta.Generator[AnyReadIo | _InternalResponse, bytes | None, None]:
        # Parse request

        gen = self._parser.coro_parse()
        sz = next(gen)
        while True:
            try:
                line = check_isinstance((yield self.ReadLineIo(sz)), bytes)
                sz = gen.send(line)
            except StopIteration as e:
                parsed = e.value
                break

        if isinstance(parsed, EmptyParsedHttpResult):
            raise EOFError

        if isinstance(parsed, ParseHttpRequestError):
            yield self._build_error_internal_response(
                parsed.code,
                *parsed.message,
                version=parsed.version,
            )
            return

        parsed = check_isinstance(parsed, ParsedHttpRequest)

        # Log

        self._logging.log_message(self._logging_context, '%r', parsed)

        # Handle CONTINUE

        if parsed.expects_continue:
            # https://bugs.python.org/issue1491
            # https://github.com/python/cpython/commit/0f476d49f8d4aa84210392bf13b59afc67b32b31
            yield self._InternalResponse(
                version=parsed.version,
                code=http.HTTPStatus.CONTINUE,
            )

        # Read data

        request_data: bytes | None
        if (cl := parsed.headers.get('Content-Length')) is not None:
            request_data = yield self.ReadIo(int(cl))
        else:
            request_data = None

        # Build request

        request = HttpHandlerRequest(
            client_address=self._client_address,
            method=check_not_none(parsed.method),
            path=parsed.path,
            headers=parsed.headers,
            data=request_data,
        )

        # Build response

        try:
            response = self._handler(request)

        except UnsupportedMethodHttpHandlerError:
            yield self._build_error_internal_response(
                http.HTTPStatus.NOT_IMPLEMENTED,
                f'Unsupported method ({parsed.method!r})',
                version=parsed.version,
                method=parsed.method,
            )
            return

        # Build internal response

        response_headers = response.headers or {}
        response_data = response.data

        headers: list[CoroHttpServer._Header] = [
            *self._make_default_headers(),
        ]

        for k, v in response_headers.items():
            headers.append(self._Header(k, v))

        if response.close_connection and 'Connection' not in headers:
            headers.append(self._Header('Connection', 'close'))

        yield self._InternalResponse(
            version=parsed.version,
            code=http.HTTPStatus(response.status),
            headers=headers,
            data=response_data,
            close_connection=response.close_connection,
        )


##


class CoroHttpServerSocketHandler(SocketHandler):
    def __init__(
            self,
            client_address: SocketAddress,
            rfile: ta.BinaryIO,
            wfile: ta.BinaryIO,
            *,
            coro_http_server_factory: CoroHttpServerFactory,
    ) -> None:
        super().__init__(
            client_address,
            rfile,
            wfile,
        )

        self._coro_http_server_factory = coro_http_server_factory

    def handle(self) -> None:
        server = self._coro_http_server_factory(self._client_address)

        gen = server.coro_handle()

        o = next(gen)
        while True:
            if isinstance(o, CoroHttpServer.ReadIo):
                i = self._rfile.read(o.sz)
            elif isinstance(o, CoroHttpServer.ReadLineIo):
                i = self._rfile.readline(o.sz)
            elif isinstance(o, CoroHttpServer.WriteIo):
                self._wfile.write(o.data)
                self._wfile.flush()
                i = None
            else:
                raise TypeError(o)

            try:
                if i is not None:
                    o = gen.send(i)
                else:
                    o = next(gen)
            except StopIteration:
                break
