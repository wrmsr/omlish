import abc
import http.client
import http.server
import io
import typing as ta


##


def read_raw_http_headers(
        fp: ta.BinaryIO,
        *,
        max_line: int = http.client._MAXLINE,  # type: ignore  # noqa
        max_headers: int = http.client._MAXHEADERS,  # type: ignore  # noqa
) -> list[bytes]:
    """
    Reads potential header lines into a list from a file pointer.

    Length of line is limited by _MAXLINE, and number of headers is limited by _MAXHEADERS.
    """

    headers: list[bytes] = []
    while True:
        line = fp.readline(max_line + 1)
        if len(line) > max_line:
            raise http.client.LineTooLong('header line')
        headers.append(line)
        if len(headers) > max_headers:
            raise http.client.HTTPException(f'got more than {max_headers} headers')
        if line in (b'\r\n', b'\n', b''):
            break
    return headers


def parse_raw_http_headers(lst: ta.Sequence[bytes]) -> http.client.HTTPMessage:
    return http.client.parse_headers(io.BytesIO(b''.join(lst)))


##


class ParseHttpRequestResult(abc.ABC):
    def __init__(
            self,
            *,
            protocol_version: str,
            request_line: str,
            request_version: str,
            headers: http.client.HTTPMessage | None,
            close_connection: bool,
    ) -> None:
        super().__init__()

        self.protocol_version = protocol_version
        self.request_line = request_line
        self.request_version = request_version
        self.headers = headers
        self.close_connection = close_connection


class EmptyParsedHttpResult(ParseHttpRequestResult):
    pass


class ContinueParsedHttpResult(ParseHttpRequestResult):
    pass


class ParseHttpRequestError(ParseHttpRequestResult):
    def __init__(
            self,
            *,
            code: http.HTTPStatus,
            message: str | tuple[str, str],

            **kwargs: ta.Any,
    ) -> None:
        super().__init__(**kwargs)

        self.code = code
        self.message = message


class ParsedHttpRequest(ParseHttpRequestResult):
    def __init__(
            self,
            *,
            method: str,
            path: str,
            headers: http.client.HTTPMessage,

            **kwargs: ta.Any,
    ) -> None:
        super().__init__(
            headers=headers,
            **kwargs,
        )

        self.method = method
        self.path = path


#


class HttpRequestParser:
    DEFAULT_PROTOCOL_VERSION = 'HTTP/1.0'

    # The default request version. This only affects responses up until the point where the request line is parsed, so
    # it mainly decides what the client gets back when sending a malformed request line.
    # Most web servers default to HTTP 0.9, i.e. don't send a status line.
    DEFAULT_REQUEST_VERSION = 'HTTP/0.9'

    def __init__(
            self,
            *,
            protocol_version: str = DEFAULT_PROTOCOL_VERSION,
    ) -> None:
        super().__init__()

        self._protocol_version = protocol_version

    def parse(
            self,
            raw_request_line: bytes,
            read_raw_headers: ta.Callable[[], ta.Sequence[bytes]],
    ) -> ParseHttpRequestResult:
        request_line = raw_request_line.decode('iso-8859-1').rstrip('\r\n')

        #

        request_version = self.DEFAULT_REQUEST_VERSION
        headers: http.client.HTTPMessage | None = None
        close_connection = True

        def result_kwargs():
            return dict(
                request_line=request_line,
                request_version=request_version,
                headers=headers,
                close_connection=close_connection,
            )

        #

        words = request_line.split()
        if len(words) == 0:
            return EmptyParsedHttpResult(**result_kwargs())

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
                return ParseHttpRequestError(
                    code=http.HTTPStatus.BAD_REQUEST,
                    message=f'Bad request version ({version!r})',
                    **result_kwargs(),
                )

            if version_number >= (1, 1) and self._protocol_version >= 'HTTP/1.1':
                close_connection = False

            if version_number >= (2, 0):
                return ParseHttpRequestError(
                    code=http.HTTPStatus.HTTP_VERSION_NOT_SUPPORTED,
                    message=f'Invalid HTTP version ({base_version_number})',
                    close_connection=close_connection,
                )

            request_version = version

        if not 2 <= len(words) <= 3:
            return ParseHttpRequestError(
                code=http.HTTPStatus.BAD_REQUEST,
                message=f'Bad request syntax ({request_line!r})',
                **result_kwargs(),
            )

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

        # Examine the headers and look for a Connection directive.
        try:
            raw_headers = read_raw_headers()
            headers = parse_raw_http_headers(raw_headers)

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

        conn_type = headers.get('Connection', '')
        if conn_type.lower() == 'close':
            close_connection = True
        elif (
                conn_type.lower() == 'keep-alive' and
                self._protocol_version >= 'HTTP/1.1'
        ):
            close_connection = False

        # Examine the headers and look for an Expect directive
        expect = headers.get('Expect', '')
        if (
                expect.lower() == '100-continue' and
                self._protocol_version >= 'HTTP/1.1' and
                request_version >= 'HTTP/1.1'
        ):
            return ContinueParsedHttpResult(**result_kwargs())

        return ParsedHttpRequest(
            method=method,
            path=path,
            **result_kwargs(),
        )
