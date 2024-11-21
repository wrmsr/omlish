# ruff: noqa: UP006 UP007
# PYTHON SOFTWARE FOUNDATION LICENSE VERSION 2
# --------------------------------------------
#
# 1. This LICENSE AGREEMENT is between the Python Software Foundation ("PSF"), and the Individual or Organization
# ("Licensee") accessing and otherwise using this software ("Python") in source or binary form and its associated
# documentation.
#
# 2. Subject to the terms and conditions of this License Agreement, PSF hereby grants Licensee a nonexclusive,
# royalty-free, world-wide license to reproduce, analyze, test, perform and/or display publicly, prepare derivative
# works, distribute, and otherwise use Python alone or in any derivative version, provided, however, that PSF's License
# Agreement and PSF's notice of copyright, i.e., "Copyright (c) 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009,
# 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017 Python Software Foundation; All Rights Reserved" are retained in Python
# alone or in any derivative version prepared by Licensee.
#
# 3. In the event Licensee prepares a derivative work that is based on or incorporates Python or any part thereof, and
# wants to make the derivative work available to others as provided herein, then Licensee hereby agrees to include in
# any such work a brief summary of the changes made to Python.
#
# 4. PSF is making Python available to Licensee on an "AS IS" basis.  PSF MAKES NO REPRESENTATIONS OR WARRANTIES,
# EXPRESS OR IMPLIED.  BY WAY OF EXAMPLE, BUT NOT LIMITATION, PSF MAKES NO AND DISCLAIMS ANY REPRESENTATION OR WARRANTY
# OF MERCHANTABILITY OR FITNESS FOR ANY PARTICULAR PURPOSE OR THAT THE USE OF PYTHON WILL NOT INFRINGE ANY THIRD PARTY
# RIGHTS.
#
# 5. PSF SHALL NOT BE LIABLE TO LICENSEE OR ANY OTHER USERS OF PYTHON FOR ANY INCIDENTAL, SPECIAL, OR CONSEQUENTIAL
# DAMAGES OR LOSS AS A RESULT OF MODIFYING, DISTRIBUTING, OR OTHERWISE USING PYTHON, OR ANY DERIVATIVE THEREOF, EVEN IF
# ADVISED OF THE POSSIBILITY THEREOF.
#
# 6. This License Agreement will automatically terminate upon a material breach of its terms and conditions.
#
# 7. Nothing in this License Agreement shall be deemed to create any relationship of agency, partnership, or joint
# venture between PSF and Licensee.  This License Agreement does not grant permission to use PSF trademarks or trade
# name in a trademark sense to endorse or promote products or services of Licensee, or any third party.
#
# 8. By copying, installing or otherwise using Python, Licensee agrees to be bound by the terms and conditions of this
# License Agreement.
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

from ..check import check_isinstance
from ..check import check_none
from ..check import check_not_none
from ..socket import SocketAddress
from ..socket import SocketHandler
from .handlers import HttpHandler
from .handlers import HttpHandlerRequest
from .handlers import UnsupportedMethodHttpHandlerError
from .parsing import EmptyParsedHttpResult
from .parsing import HttpRequestParser
from .parsing import ParsedHttpRequest
from .parsing import ParseHttpRequestError
from .versions import HttpProtocolVersion
from .versions import HttpProtocolVersions


CoroHttpServerFactory = ta.Callable[[SocketAddress], 'CoroHttpServer']


##


class CoroHttpServer:
    """
    Adapted from stdlib:
     - https://github.com/python/cpython/blob/4b4e0dbdf49adc91c35a357ad332ab3abd4c31b1/Lib/http/server.py#L146
    """

    #

    def __init__(
            self,
            client_address: SocketAddress,
            *,
            handler: HttpHandler,
            parser: HttpRequestParser = HttpRequestParser(),

            default_content_type: ta.Optional[str] = None,

            error_message_format: ta.Optional[str] = None,
            error_content_type: ta.Optional[str] = None,
    ) -> None:
        super().__init__()

        self._client_address = client_address

        self._handler = handler
        self._parser = parser

        self._default_content_type = default_content_type or self.DEFAULT_CONTENT_TYPE

        self._error_message_format = error_message_format or self.DEFAULT_ERROR_MESSAGE
        self._error_content_type = error_content_type or self.DEFAULT_ERROR_CONTENT_TYPE

    #

    @property
    def client_address(self) -> SocketAddress:
        return self._client_address

    @property
    def handler(self) -> HttpHandler:
        return self._handler

    @property
    def parser(self) -> HttpRequestParser:
        return self._parser

    #

    def _format_timestamp(self, timestamp: ta.Optional[float] = None) -> str:
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

    def _get_header_close_connection_action(self, h: _Header) -> ta.Optional[bool]:
        if h.key.lower() != 'connection':
            return None
        elif h.value.lower() == 'close':
            return True
        elif h.value.lower() == 'keep-alive':
            return False
        else:
            return None

    def _make_default_headers(self) -> ta.List[_Header]:
        return [
            self._Header('Date', self._format_timestamp()),
        ]

    #

    _STATUS_RESPONSES: ta.Mapping[int, ta.Tuple[str, str]] = {
        v: (v.phrase, v.description)
        for v in http.HTTPStatus.__members__.values()
    }

    def _format_status_line(
            self,
            version: HttpProtocolVersion,
            code: ta.Union[http.HTTPStatus, int],
            message: ta.Optional[str] = None,
    ) -> str:
        if message is None:
            if code in self._STATUS_RESPONSES:
                message = self._STATUS_RESPONSES[code][0]
            else:
                message = ''

        return f'{version} {int(code)} {message}\r\n'

    #

    @dc.dataclass(frozen=True)
    class _Response:
        version: HttpProtocolVersion
        code: http.HTTPStatus

        message: ta.Optional[str] = None
        headers: ta.Optional[ta.Sequence['CoroHttpServer._Header']] = None
        data: ta.Optional[bytes] = None
        close_connection: ta.Optional[bool] = False

        def get_header(self, key: str) -> ta.Optional['CoroHttpServer._Header']:
            for h in self.headers or []:
                if h.key.lower() == key.lower():
                    return h
            return None

    #

    def _build_response_bytes(self, a: _Response) -> bytes:
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

    def _preprocess_response(self, resp: _Response) -> _Response:
        nh: ta.List[CoroHttpServer._Header] = []
        kw: ta.Dict[str, ta.Any] = {}

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

    @dc.dataclass(frozen=True)
    class Error:
        version: HttpProtocolVersion
        code: http.HTTPStatus
        message: str
        explain: str

        method: ta.Optional[str] = None

    def _build_error(
            self,
            code: ta.Union[http.HTTPStatus, int],
            message: ta.Optional[str] = None,
            explain: ta.Optional[str] = None,
            *,
            version: ta.Optional[HttpProtocolVersion] = None,
            method: ta.Optional[str] = None,
    ) -> Error:
        code = http.HTTPStatus(code)

        try:
            short_msg, long_msg = self._STATUS_RESPONSES[code]
        except KeyError:
            short_msg, long_msg = '???', '???'
        if message is None:
            message = short_msg
        if explain is None:
            explain = long_msg

        if version is None:
            version = self._parser.server_version

        return self.Error(
            version=version,
            code=code,
            message=message,
            explain=explain,

            method=method,
        )

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

    def _build_error_response(self, err: Error) -> _Response:
        headers: ta.List[CoroHttpServer._Header] = [
            *self._make_default_headers(),
            self._Header('Connection', 'close'),
        ]

        # Message body is omitted for cases described in:
        #  - RFC7230: 3.3. 1xx, 204(No Content), 304(Not Modified)
        #  - RFC7231: 6.3.6. 205(Reset Content)
        data: ta.Optional[bytes] = None
        if (
                err.code >= http.HTTPStatus.OK and
                err.code not in (
                    http.HTTPStatus.NO_CONTENT,
                    http.HTTPStatus.RESET_CONTENT,
                    http.HTTPStatus.NOT_MODIFIED,
                )
        ):
            # HTML encode to prevent Cross Site Scripting attacks (see bug #1100201)
            content = self._error_message_format.format(
                code=err.code,
                message=html.escape(err.message, quote=False),
                explain=html.escape(err.explain, quote=False),
            )
            body = content.encode('UTF-8', 'replace')

            headers.extend([
                self._Header('Content-Type', self._error_content_type),
                self._Header('Content-Length', str(len(body))),
            ])

            if err.method != 'HEAD' and body:
                data = body

        return self._Response(
            version=err.version,
            code=err.code,
            message=err.message,
            headers=headers,
            data=data,
            close_connection=True,
        )

    #

    class Io(abc.ABC):  # noqa
        pass

    #

    class AnyLogIo(Io):
        pass

    @dc.dataclass(frozen=True)
    class ParsedRequestLogIo(AnyLogIo):
        request: ParsedHttpRequest

    @dc.dataclass(frozen=True)
    class ErrorLogIo(AnyLogIo):
        error: 'CoroHttpServer.Error'

    #

    class AnyReadIo(Io):  # noqa
        pass

    @dc.dataclass(frozen=True)
    class ReadIo(AnyReadIo):
        sz: int

    @dc.dataclass(frozen=True)
    class ReadLineIo(AnyReadIo):
        sz: int

    #

    @dc.dataclass(frozen=True)
    class WriteIo(Io):
        data: bytes

    #

    def coro_handle(self) -> ta.Generator[Io, ta.Optional[bytes], None]:
        while True:
            gen = self.coro_handle_one()

            o = next(gen)
            i: ta.Optional[bytes]
            while True:
                if isinstance(o, self.AnyLogIo):
                    i = None
                    yield o

                elif isinstance(o, self.AnyReadIo):
                    i = check_isinstance((yield o), bytes)

                elif isinstance(o, self._Response):
                    i = None
                    r = self._preprocess_response(o)
                    b = self._build_response_bytes(r)
                    check_none((yield self.WriteIo(b)))

                else:
                    raise TypeError(o)

                try:
                    o = gen.send(i)
                except EOFError:
                    return
                except StopIteration:
                    break

    def coro_handle_one(self) -> ta.Generator[
        ta.Union[AnyLogIo, AnyReadIo, _Response],
        ta.Optional[bytes],
        None,
    ]:
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
            raise EOFError  # noqa

        if isinstance(parsed, ParseHttpRequestError):
            err = self._build_error(
                parsed.code,
                *parsed.message,
                version=parsed.version,
            )
            yield self.ErrorLogIo(err)
            yield self._build_error_response(err)
            return

        parsed = check_isinstance(parsed, ParsedHttpRequest)

        # Log

        check_none((yield self.ParsedRequestLogIo(parsed)))

        # Handle CONTINUE

        if parsed.expects_continue:
            # https://bugs.python.org/issue1491
            # https://github.com/python/cpython/commit/0f476d49f8d4aa84210392bf13b59afc67b32b31
            yield self._Response(
                version=parsed.version,
                code=http.HTTPStatus.CONTINUE,
            )

        # Read data

        request_data: ta.Optional[bytes]
        if (cl := parsed.headers.get('Content-Length')) is not None:
            request_data = check_isinstance((yield self.ReadIo(int(cl))), bytes)
        else:
            request_data = None

        # Build request

        handler_request = HttpHandlerRequest(
            client_address=self._client_address,
            method=check_not_none(parsed.method),
            path=parsed.path,
            headers=parsed.headers,
            data=request_data,
        )

        # Build handler response

        try:
            handler_response = self._handler(handler_request)

        except UnsupportedMethodHttpHandlerError:
            err = self._build_error(
                http.HTTPStatus.NOT_IMPLEMENTED,
                f'Unsupported method ({parsed.method!r})',
                version=parsed.version,
                method=parsed.method,
            )
            yield self.ErrorLogIo(err)
            yield self._build_error_response(err)
            return

        # Build internal response

        response_headers = handler_response.headers or {}
        response_data = handler_response.data

        headers: ta.List[CoroHttpServer._Header] = [
            *self._make_default_headers(),
        ]

        for k, v in response_headers.items():
            headers.append(self._Header(k, v))

        if handler_response.close_connection and 'Connection' not in headers:
            headers.append(self._Header('Connection', 'close'))

        yield self._Response(
            version=parsed.version,
            code=http.HTTPStatus(handler_response.status),
            headers=headers,
            data=response_data,
            close_connection=handler_response.close_connection,
        )


##


class CoroHttpServerSocketHandler(SocketHandler):
    def __init__(
            self,
            client_address: SocketAddress,
            rfile: ta.BinaryIO,
            wfile: ta.BinaryIO,
            *,
            server_factory: CoroHttpServerFactory,
            log_handler: ta.Optional[ta.Callable[[CoroHttpServer, CoroHttpServer.AnyLogIo], None]] = None,
    ) -> None:
        super().__init__(
            client_address,
            rfile,
            wfile,
        )

        self._server_factory = server_factory
        self._log_handler = log_handler

    def handle(self) -> None:
        server = self._server_factory(self._client_address)

        gen = server.coro_handle()

        o = next(gen)
        while True:
            if isinstance(o, CoroHttpServer.AnyLogIo):
                i = None
                if self._log_handler is not None:
                    self._log_handler(server, o)

            elif isinstance(o, CoroHttpServer.ReadIo):
                i = self._rfile.read(o.sz)

            elif isinstance(o, CoroHttpServer.ReadLineIo):
                i = self._rfile.readline(o.sz)

            elif isinstance(o, CoroHttpServer.WriteIo):
                i = None
                self._wfile.write(o.data)
                self._wfile.flush()

            else:
                raise TypeError(o)

            try:
                if i is not None:
                    o = gen.send(i)
                else:
                    o = next(gen)
            except StopIteration:
                break
