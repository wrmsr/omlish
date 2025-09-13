# ruff: noqa: UP006 UP007 UP043 UP045
# @omlish-lite
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
import dataclasses as dc
import email.utils
import html
import http
import io
import textwrap
import time
import typing as ta

from ....lite.check import check
from ....sockets.addresses import SocketAddress
from ...handlers import HttpHandler
from ...handlers import HttpHandlerRequest
from ...handlers import HttpHandlerResponseData
from ...handlers import HttpHandlerResponseStreamedData
from ...handlers import UnsupportedMethodHttpHandlerError
from ...parsing import EmptyParsedHttpResult
from ...parsing import HttpRequestParser
from ...parsing import ParsedHttpRequest
from ...parsing import ParseHttpRequestError
from ...versions import HttpProtocolVersion
from ...versions import HttpProtocolVersions
from ..io import CoroHttpIo


CoroHttpServerFactory = ta.Callable[[SocketAddress], 'CoroHttpServer']  # ta.TypeAlias


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
        data: ta.Optional[HttpHandlerResponseData] = None
        close_connection: ta.Optional[bool] = False

        def get_header(self, key: str) -> ta.Optional['CoroHttpServer._Header']:
            for h in self.headers or []:
                if h.key.lower() == key.lower():
                    return h
            return None

        def close(self) -> None:
            if isinstance(d := self.data, HttpHandlerResponseStreamedData):
                d.close()

    #

    def _build_response_head_bytes(self, a: _Response) -> bytes:
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

        return out.getvalue()

    def _yield_response_data(self, a: _Response) -> ta.Iterator[bytes]:
        if a.data is None:
            return

        elif isinstance(a.data, bytes):
            yield a.data
            return

        elif isinstance(a.data, HttpHandlerResponseStreamedData):
            yield from a.data.iter

        else:
            raise TypeError(a.data)

    #

    DEFAULT_CONTENT_TYPE = 'text/plain'

    def _preprocess_response(self, resp: _Response) -> _Response:
        nh: ta.List[CoroHttpServer._Header] = []
        kw: ta.Dict[str, ta.Any] = {}

        if resp.get_header('Content-Type') is None:
            nh.append(self._Header('Content-Type', self._default_content_type))

        if resp.data is not None and resp.get_header('Content-Length') is None:
            cl: ta.Optional[int]
            if isinstance(resp.data, bytes):
                cl = len(resp.data)
            elif isinstance(resp.data, HttpHandlerResponseStreamedData):
                cl = resp.data.length
            else:
                raise TypeError(resp.data)
            if cl is not None:
                nh.append(self._Header('Content-Length', str(cl)))

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

    @dc.dataclass(frozen=True)
    class ParsedRequestLogIo(CoroHttpIo.AnyLogIo):
        request: ParsedHttpRequest

    @dc.dataclass(frozen=True)
    class ErrorLogIo(CoroHttpIo.AnyLogIo):
        error: 'CoroHttpServer.Error'

    #

    @dc.dataclass(frozen=True)
    class CoroHandleResult:
        close_reason: ta.Literal['response', 'internal', None] = None

    def coro_handle(self) -> ta.Generator[CoroHttpIo.Io, ta.Optional[bytes], CoroHandleResult]:
        return self._coro_run_handler(self._coro_handle_one())

    class Close(Exception):  # noqa
        pass

    def _coro_run_handler(
            self,
            gen: ta.Generator[
                ta.Union[CoroHttpIo.AnyLogIo, CoroHttpIo.AnyReadIo, _Response],
                ta.Optional[bytes],
                None,
            ],
    ) -> ta.Generator[CoroHttpIo.Io, ta.Optional[bytes], CoroHandleResult]:
        i: ta.Optional[bytes]
        o: ta.Any = next(gen)
        while True:
            try:
                if isinstance(o, CoroHttpIo.AnyLogIo):
                    i = None
                    yield o

                elif isinstance(o, CoroHttpIo.AnyReadIo):
                    i = check.isinstance((yield o), bytes)

                elif isinstance(o, self._Response):
                    i = None

                    r = self._preprocess_response(o)
                    hb = self._build_response_head_bytes(r)
                    check.none((yield CoroHttpIo.WriteIo(hb)))

                    for b in self._yield_response_data(r):
                        yield CoroHttpIo.WriteIo(b)

                    o.close()
                    if o.close_connection:
                        return self.CoroHandleResult(
                            close_reason='response',
                        )
                    o = None

                else:
                    raise TypeError(o)  # noqa

                try:
                    o = gen.send(i)
                except self.Close:
                    return self.CoroHandleResult(
                        close_reason='internal',
                    )
                except StopIteration:
                    return self.CoroHandleResult()

            except Exception:  # noqa
                if hasattr(o, 'close'):
                    o.close()

                raise

    def _coro_handle_one(self) -> ta.Generator[
        ta.Union[CoroHttpIo.AnyLogIo, CoroHttpIo.AnyReadIo, _Response],
        ta.Optional[bytes],
        None,
    ]:
        # Parse request

        gen = self._parser.coro_parse()
        sz = next(gen)
        while True:
            try:
                line = check.isinstance((yield CoroHttpIo.ReadLineIo(sz)), bytes)
                sz = gen.send(line)
            except StopIteration as e:
                parsed = e.value
                break

        if isinstance(parsed, EmptyParsedHttpResult):
            raise self.Close

        if isinstance(parsed, ParseHttpRequestError):
            err = self._build_error(
                parsed.code,
                *([parsed.message] if isinstance(parsed.message, str) else parsed.message),
                version=parsed.version,
            )
            yield self.ErrorLogIo(err)
            yield self._build_error_response(err)
            return

        parsed = check.isinstance(parsed, ParsedHttpRequest)

        # Log

        check.none((yield self.ParsedRequestLogIo(parsed)))

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
            request_data = check.isinstance((yield CoroHttpIo.ReadIo(int(cl))), bytes)
        else:
            request_data = None

        # Build request

        handler_request = HttpHandlerRequest(
            client_address=self._client_address,
            method=check.not_none(parsed.method),
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

        try:
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

        except Exception:  # noqa
            handler_response.close()

            raise
