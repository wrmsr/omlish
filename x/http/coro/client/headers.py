# @omlish-lite
# ruff: noqa: UP006 UP007
import email.message
import email.parser
import typing as ta

from omlish.lite.check import check

from .errors import CoroHttpClientErrors
from .io import CoroHttpClientIo


##


class CoroHttpClientHeaders:
    def __new__(cls, *args, **kwargs):  # noqa
        raise TypeError

    #

    MAX_HEADERS: ta.ClassVar[int] = 100

    @classmethod
    def read_headers(cls) -> ta.Generator[CoroHttpClientIo.Io, ta.Optional[bytes], ta.List[bytes]]:
        """
        Reads potential header lines into a list from a file pointer.

        Length of line is limited by MAX_LINE, and number of headers is limited by MAX_HEADERS.
        """

        headers = []
        while True:
            line = check.isinstance((yield CoroHttpClientIo.ReadLineIo(CoroHttpClientIo.MAX_LINE + 1)), bytes)
            if len(line) > CoroHttpClientIo.MAX_LINE:
                raise CoroHttpClientErrors.LineTooLongError(CoroHttpClientErrors.LineTooLongError.LineType.HEADER)

            headers.append(line)
            if len(headers) > cls.MAX_HEADERS:
                raise CoroHttpClientErrors.ClientError(f'got more than {cls.MAX_HEADERS} headers')

            if line in (b'\r\n', b'\n', b''):
                break

        return headers

    @classmethod
    def parse_header_lines(cls, header_lines: ta.Sequence[bytes]) -> email.message.Message:
        """
        Parses only RFC2822 headers from header lines.

        email Parser wants to see strings rather than bytes. But a TextIOWrapper around self.rfile would buffer too many
        bytes from the stream, bytes which we later need to read as bytes. So we read the correct bytes here, as bytes,
        for email Parser to parse.
        """

        text = b''.join(header_lines).decode('iso-8859-1')
        return email.parser.Parser().parsestr(text)

    @classmethod
    def parse_headers(cls) -> ta.Generator[CoroHttpClientIo.Io, ta.Optional[bytes], email.message.Message]:
        """Parses only RFC2822 headers from a file pointer."""

        headers = yield from cls.read_headers()
        return cls.parse_header_lines(headers)
