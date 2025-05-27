# ruff: noqa: UP006 UP007
import typing as ta

from omlish.lite.check import check

from .consts import MAX_LINE
from .errors import BadStatusLineError
from .errors import LineTooLongError
from .errors import RemoteDisconnectedError
from .io import Io
from .io import ReadLineIo


#

class StatusLine(ta.NamedTuple):
    version: str
    status: int
    reason: str


def read_status_line() -> ta.Generator[Io, ta.Optional[bytes], StatusLine]:
    line = str(check.isinstance((yield ReadLineIo(MAX_LINE + 1)), bytes), 'iso-8859-1')
    if len(line) > MAX_LINE:
        raise LineTooLongError(LineTooLongError.LineType.STATUS)
    if not line:
        # Presumably, the server closed the connection before sending a valid response.
        raise RemoteDisconnectedError('Remote end closed connection without response')

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
        raise BadStatusLineError(line)

    # The status code is a three-digit number
    try:
        status = int(status_str)
    except ValueError:
        raise BadStatusLineError(line) from None

    if status < 100 or status > 999:
        raise BadStatusLineError(line)

    return StatusLine(version, status, reason)
