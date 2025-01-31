# ruff: noqa: UP006 UP007
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
import abc
import http.client
import http.server
import io
import typing as ta

from .versions import HttpProtocolVersion
from .versions import HttpProtocolVersions


T = ta.TypeVar('T')


HttpHeaders = http.client.HTTPMessage  # ta.TypeAlias


##


class ParseHttpRequestResult(abc.ABC):  # noqa
    __slots__ = (
        'server_version',
        'request_line',
        'request_version',
        'version',
        'headers',
        'close_connection',
    )

    def __init__(
            self,
            *,
            server_version: HttpProtocolVersion,
            request_line: str,
            request_version: HttpProtocolVersion,
            version: HttpProtocolVersion,
            headers: ta.Optional[HttpHeaders],
            close_connection: bool,
    ) -> None:
        super().__init__()

        self.server_version = server_version
        self.request_line = request_line
        self.request_version = request_version
        self.version = version
        self.headers = headers
        self.close_connection = close_connection

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({", ".join(f"{a}={getattr(self, a)!r}" for a in self.__slots__)})'


class EmptyParsedHttpResult(ParseHttpRequestResult):
    pass


class ParseHttpRequestError(ParseHttpRequestResult):
    __slots__ = (
        'code',
        'message',
        *ParseHttpRequestResult.__slots__,
    )

    def __init__(
            self,
            *,
            code: http.HTTPStatus,
            message: ta.Union[str, ta.Tuple[str, str]],

            **kwargs: ta.Any,
    ) -> None:
        super().__init__(**kwargs)

        self.code = code
        self.message = message


class ParsedHttpRequest(ParseHttpRequestResult):
    __slots__ = (
        'method',
        'path',
        'headers',
        'expects_continue',
        *[a for a in ParseHttpRequestResult.__slots__ if a != 'headers'],
    )

    def __init__(
            self,
            *,
            method: str,
            path: str,
            headers: HttpHeaders,
            expects_continue: bool,

            **kwargs: ta.Any,
    ) -> None:
        super().__init__(
            headers=headers,
            **kwargs,
        )

        self.method = method
        self.path = path
        self.expects_continue = expects_continue

    headers: HttpHeaders


#


class HttpRequestParser:
    DEFAULT_SERVER_VERSION = HttpProtocolVersions.HTTP_1_0

    # The default request version. This only affects responses up until the point where the request line is parsed, so
    # it mainly decides what the client gets back when sending a malformed request line.
    # Most web servers default to HTTP 0.9, i.e. don't send a status line.
    DEFAULT_REQUEST_VERSION = HttpProtocolVersions.HTTP_0_9

    #

    DEFAULT_MAX_LINE: int = 0x10000
    DEFAULT_MAX_HEADERS: int = 100

    #

    def __init__(
            self,
            *,
            server_version: HttpProtocolVersion = DEFAULT_SERVER_VERSION,

            max_line: int = DEFAULT_MAX_LINE,
            max_headers: int = DEFAULT_MAX_HEADERS,
    ) -> None:
        super().__init__()

        if server_version >= HttpProtocolVersions.HTTP_2_0:
            raise ValueError(f'Unsupported protocol version: {server_version}')
        self._server_version = server_version

        self._max_line = max_line
        self._max_headers = max_headers

    #

    @property
    def server_version(self) -> HttpProtocolVersion:
        return self._server_version

    #

    def _run_read_line_coro(
            self,
            gen: ta.Generator[int, bytes, T],
            read_line: ta.Callable[[int], bytes],
    ) -> T:
        sz = next(gen)
        while True:
            try:
                sz = gen.send(read_line(sz))
            except StopIteration as e:
                return e.value

    #

    def parse_request_version(self, version_str: str) -> HttpProtocolVersion:
        if not version_str.startswith('HTTP/'):
            raise ValueError(version_str)  # noqa

        base_version_number = version_str.split('/', 1)[1]
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

        return HttpProtocolVersion(
            int(version_number_parts[0]),
            int(version_number_parts[1]),
        )

    #

    def coro_read_raw_headers(self) -> ta.Generator[int, bytes, ta.List[bytes]]:
        raw_headers: ta.List[bytes] = []
        while True:
            line = yield self._max_line + 1
            if len(line) > self._max_line:
                raise http.client.LineTooLong('header line')
            raw_headers.append(line)
            if len(raw_headers) > self._max_headers:
                raise http.client.HTTPException(f'got more than {self._max_headers} headers')
            if line in (b'\r\n', b'\n', b''):
                break
        return raw_headers

    def read_raw_headers(self, read_line: ta.Callable[[int], bytes]) -> ta.List[bytes]:
        return self._run_read_line_coro(self.coro_read_raw_headers(), read_line)

    def parse_raw_headers(self, raw_headers: ta.Sequence[bytes]) -> HttpHeaders:
        return http.client.parse_headers(io.BytesIO(b''.join(raw_headers)))

    #

    _TLS_HANDSHAKE_PREFIX = b'\x16'

    def coro_parse(self) -> ta.Generator[int, bytes, ParseHttpRequestResult]:
        raw_request_line = yield self._max_line + 1

        # Common result kwargs

        request_line = '-'
        request_version = self.DEFAULT_REQUEST_VERSION

        # Set to min(server, request) when it gets that far, but if it fails before that the server authoritatively
        # responds with its own version.
        version = self._server_version

        headers: HttpHeaders | None = None

        close_connection = True

        def result_kwargs():
            return dict(
                server_version=self._server_version,
                request_line=request_line,
                request_version=request_version,
                version=version,
                headers=headers,
                close_connection=close_connection,
            )

        # Decode line

        if len(raw_request_line) > self._max_line:
            return ParseHttpRequestError(
                code=http.HTTPStatus.REQUEST_URI_TOO_LONG,
                message='Request line too long',
                **result_kwargs(),
            )

        if not raw_request_line:
            return EmptyParsedHttpResult(**result_kwargs())

        # Detect TLS

        if raw_request_line.startswith(self._TLS_HANDSHAKE_PREFIX):
            return ParseHttpRequestError(
                code=http.HTTPStatus.BAD_REQUEST,
                message='Bad request version (probable TLS handshake)',
                **result_kwargs(),
            )

        # Decode line

        request_line = raw_request_line.decode('iso-8859-1').rstrip('\r\n')

        # Split words

        words = request_line.split()
        if len(words) == 0:
            return EmptyParsedHttpResult(**result_kwargs())

        # Parse and set version

        if len(words) >= 3:  # Enough to determine protocol version
            version_str = words[-1]
            try:
                request_version = self.parse_request_version(version_str)

            except (ValueError, IndexError):
                return ParseHttpRequestError(
                    code=http.HTTPStatus.BAD_REQUEST,
                    message=f'Bad request version ({version_str!r})',
                    **result_kwargs(),
                )

            if (
                    request_version < HttpProtocolVersions.HTTP_0_9 or
                    request_version >= HttpProtocolVersions.HTTP_2_0
            ):
                return ParseHttpRequestError(
                    code=http.HTTPStatus.HTTP_VERSION_NOT_SUPPORTED,
                    message=f'Invalid HTTP version ({version_str})',
                    **result_kwargs(),
                )

            version = min([self._server_version, request_version])

            if version >= HttpProtocolVersions.HTTP_1_1:
                close_connection = False

        # Verify word count

        if not 2 <= len(words) <= 3:
            return ParseHttpRequestError(
                code=http.HTTPStatus.BAD_REQUEST,
                message=f'Bad request syntax ({request_line!r})',
                **result_kwargs(),
            )

        # Parse method and path

        method, path = words[:2]
        if len(words) == 2:
            close_connection = True
            if method != 'GET':
                return ParseHttpRequestError(
                    code=http.HTTPStatus.BAD_REQUEST,
                    message=f'Bad HTTP/0.9 request type ({method!r})',
                    **result_kwargs(),
                )

        # gh-87389: The purpose of replacing '//' with '/' is to protect against open redirect attacks possibly
        # triggered if the path starts with '//' because http clients treat //path as an absolute URI without scheme
        # (similar to http://path) rather than a path.
        if path.startswith('//'):
            path = '/' + path.lstrip('/')  # Reduce to a single /

        # Parse headers

        try:
            raw_gen = self.coro_read_raw_headers()
            raw_sz = next(raw_gen)
            while True:
                buf = yield raw_sz
                try:
                    raw_sz = raw_gen.send(buf)
                except StopIteration as e:
                    raw_headers = e.value
                    break

            headers = self.parse_raw_headers(raw_headers)

        except http.client.LineTooLong as err:
            return ParseHttpRequestError(
                code=http.HTTPStatus.REQUEST_HEADER_FIELDS_TOO_LARGE,
                message=('Line too long', str(err)),
                **result_kwargs(),
            )

        except http.client.HTTPException as err:
            return ParseHttpRequestError(
                code=http.HTTPStatus.REQUEST_HEADER_FIELDS_TOO_LARGE,
                message=('Too many headers', str(err)),
                **result_kwargs(),
            )

        # Check for connection directive

        conn_type = headers.get('Connection', '')
        if conn_type.lower() == 'close':
            close_connection = True
        elif (
                conn_type.lower() == 'keep-alive' and
                version >= HttpProtocolVersions.HTTP_1_1
        ):
            close_connection = False

        # Check for expect directive

        expect = headers.get('Expect', '')
        if (
                expect.lower() == '100-continue' and
                version >= HttpProtocolVersions.HTTP_1_1
        ):
            expects_continue = True
        else:
            expects_continue = False

        # Return

        return ParsedHttpRequest(
            method=method,
            path=path,
            expects_continue=expects_continue,
            **result_kwargs(),
        )

    def parse(self, read_line: ta.Callable[[int], bytes]) -> ParseHttpRequestResult:
        return self._run_read_line_coro(self.coro_parse(), read_line)
