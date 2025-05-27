# ruff: noqa: UP006 UP007
import email.message
import email.parser
import typing as ta

from omlish.lite.check import check

from .consts import MAX_HEADERS
from .consts import MAX_LINE
from .errors import ClientError
from .errors import LineTooLongError
from .io import Io
from .io import ReadLineIo


##


def read_headers() -> ta.Generator[Io, ta.Optional[bytes], ta.List[bytes]]:
    """
    Reads potential header lines into a list from a file pointer.

    Length of line is limited by MAX_LINE, and number of headers is limited by MAX_HEADERS.
    """

    headers = []
    while True:
        line = check.isinstance((yield ReadLineIo(MAX_LINE + 1)), bytes)
        if len(line) > MAX_LINE:
            raise LineTooLongError(LineTooLongError.LineType.HEADER)

        headers.append(line)
        if len(headers) > MAX_HEADERS:
            raise ClientError(f'got more than {MAX_HEADERS} headers')

        if line in (b'\r\n', b'\n', b''):
            break

    return headers


def parse_header_lines(header_lines: ta.Sequence[bytes]) -> email.message.Message:
    """
    Parses only RFC2822 headers from header lines.

    email Parser wants to see strings rather than bytes. But a TextIOWrapper around self.rfile would buffer too many
    bytes from the stream, bytes which we later need to read as bytes. So we read the correct bytes here, as bytes, for
    email Parser to parse.
    """

    text = b''.join(header_lines).decode('iso-8859-1')
    return email.parser.Parser().parsestr(text)


def parse_headers() -> ta.Generator[Io, ta.Optional[bytes], email.message.Message]:
    """Parses only RFC2822 headers from a file pointer."""

    headers = yield from read_headers()
    return parse_header_lines(headers)
