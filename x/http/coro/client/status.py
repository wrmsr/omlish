# ruff: noqa: UP006 UP007
import typing as ta

from omlish.lite.check import check

from .errors import CoroHttpClientErrors
from .io import CoroHttpClientIo


#


class CoroHttpClientStatusLine(ta.NamedTuple):
    version: str
    status: int
    reason: str

    @classmethod
    def read(cls) -> ta.Generator[CoroHttpClientIo.Io, ta.Optional[bytes], 'CoroHttpClientStatusLine']:
        line = str(check.isinstance((yield CoroHttpClientIo.ReadLineIo(CoroHttpClientIo.MAX_LINE + 1)), bytes), 'iso-8859-1')  # noqa
        if len(line) > CoroHttpClientIo.MAX_LINE:
            raise CoroHttpClientErrors.LineTooLongError(CoroHttpClientErrors.LineTooLongError.LineType.STATUS)
        if not line:
            # Presumably, the server closed the connection before sending a valid response.
            raise CoroHttpClientErrors.RemoteDisconnectedError('Remote end closed connection without response')

        version = ''
        reason = ''
        status_str = ''
        try:
            version, status_str, reason = line.split(None, 2)
        except ValueError:
            try:
                version, status_str = line.split(None, 1)
            except ValueError:
                # empty version will cause next test to fail.
                pass

        if not version.startswith('HTTP/'):
            raise CoroHttpClientErrors.BadStatusLineError(line)

        # The status code is a three-digit number
        try:
            status = int(status_str)
        except ValueError:
            raise CoroHttpClientErrors.BadStatusLineError(line) from None

        if status < 100 or status > 999:
            raise CoroHttpClientErrors.BadStatusLineError(line)

        return cls(version, status, reason)
