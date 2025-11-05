import dataclasses as dc
import io
import os
import sys
import typing as ta


##


COLORIZE = True


@dc.dataclass(frozen=True)
class AnsiColors:
    RESET: str = '\x1b[0m'

    BLACK: str = '\x1b[30m'
    BLUE: str = '\x1b[34m'
    CYAN: str = '\x1b[36m'
    GREEN: str = '\x1b[32m'
    GREY: str = '\x1b[90m'
    MAGENTA: str = '\x1b[35m'
    RED: str = '\x1b[31m'
    WHITE: str = '\x1b[37m'  # more like LIGHT GRAY
    YELLOW: str = '\x1b[33m'

    BOLD: str = '\x1b[1m'
    BOLD_BLACK: str = '\x1b[1;30m'  # DARK GRAY
    BOLD_BLUE: str = '\x1b[1;34m'
    BOLD_CYAN: str = '\x1b[1;36m'
    BOLD_GREEN: str = '\x1b[1;32m'
    BOLD_MAGENTA: str = '\x1b[1;35m'
    BOLD_RED: str = '\x1b[1;31m'
    BOLD_WHITE: str = '\x1b[1;37m'  # actual WHITE
    BOLD_YELLOW: str = '\x1b[1;33m'

    # intense: str = like bold but without being bold
    INTENSE_BLACK: str = '\x1b[90m'
    INTENSE_BLUE: str = '\x1b[94m'
    INTENSE_CYAN: str = '\x1b[96m'
    INTENSE_GREEN: str = '\x1b[92m'
    INTENSE_MAGENTA: str = '\x1b[95m'
    INTENSE_RED: str = '\x1b[91m'
    INTENSE_WHITE: str = '\x1b[97m'
    INTENSE_YELLOW: str = '\x1b[93m'

    BACKGROUND_BLACK: str = '\x1b[40m'
    BACKGROUND_BLUE: str = '\x1b[44m'
    BACKGROUND_CYAN: str = '\x1b[46m'
    BACKGROUND_GREEN: str = '\x1b[42m'
    BACKGROUND_MAGENTA: str = '\x1b[45m'
    BACKGROUND_RED: str = '\x1b[41m'
    BACKGROUND_WHITE: str = '\x1b[47m'
    BACKGROUND_YELLOW: str = '\x1b[43m'

    INTENSE_BACKGROUND_BLACK: str = '\x1b[100m'
    INTENSE_BACKGROUND_BLUE: str = '\x1b[104m'
    INTENSE_BACKGROUND_CYAN: str = '\x1b[106m'
    INTENSE_BACKGROUND_GREEN: str = '\x1b[102m'
    INTENSE_BACKGROUND_MAGENTA: str = '\x1b[105m'
    INTENSE_BACKGROUND_RED: str = '\x1b[101m'
    INTENSE_BACKGROUND_WHITE: str = '\x1b[107m'
    INTENSE_BACKGROUND_YELLOW: str = '\x1b[103m'


ANSI_COLORS = AnsiColors()

COLOR_CODES = {f.name for f in dc.fields(AnsiColors)}

NO_COLORS = AnsiColors(**{c: '' for c in COLOR_CODES})


def get_colors(
        colorize: bool = False,
        *,
        file: ta.IO[str] | ta.IO[bytes] | None = None,
) -> AnsiColors:
    if colorize or can_colorize(file=file):
        return ANSI_COLORS
    else:
        return NO_COLORS


def decolor(text: str) -> str:
    """Remove ANSI color codes from a string."""

    for code in COLOR_CODES:
        text = text.replace(code, '')
    return text


def can_colorize(*, file: ta.IO[str] | ta.IO[bytes] | None = None) -> bool:
    def _safe_getenv(k: str, fallback: str | None = None) -> str | None:
        """Exception-safe environment retrieval. See gh-128636."""

        try:
            return os.environ.get(k, fallback)
        except Exception:  # noqa
            return fallback

    if file is None:
        file = sys.stdout

    if not sys.flags.ignore_environment:
        if _safe_getenv('PYTHON_COLORS') == '0':
            return False

        if _safe_getenv('PYTHON_COLORS') == '1':
            return True

    if _safe_getenv('NO_COLOR'):
        return False

    if not COLORIZE:
        return False

    if _safe_getenv('FORCE_COLOR'):
        return True

    if _safe_getenv('TERM') == 'dumb':
        return False

    if not hasattr(file, 'fileno'):
        return False

    if sys.platform == 'win32':
        raise OSError

    try:
        return os.isatty(file.fileno())
    except io.UnsupportedOperation:
        return hasattr(file, 'isatty') and file.isatty()
