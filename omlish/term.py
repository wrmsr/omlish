import enum
import re
import sys
import time
import typing as ta

from . import lang


T = ta.TypeVar('T')


##


ESC = '\x1b'
BEL = '\x07'

DCS = ESC + 'P'
CSI = ESC + '['
ST = ESC + '\\'
OSC = ESC + ']'
RIS = ESC + 'c'


def set_title(title: str) -> str:
    return OSC + '0;' + title + BEL


def strip_ansi_codes(s: str) -> str:
    return re.sub(r'\033\[([0-9]+)(;[0-9]+)*m', '', s)


class ControlSequence:

    def __init__(self, fn: ta.Callable[..., str], desc: str) -> None:
        super().__init__()
        self._fn = fn
        self._desc = desc

    @property
    def description(self) -> str:
        return self._desc

    def __call__(self, *args, **kwargs) -> str:
        return self._fn(*args, **kwargs)


CUU = ControlSequence(lambda n: CSI + str(n) + 'A', 'Cursor Up')
CUD = ControlSequence(lambda n: CSI + str(n) + 'B', 'Cursor Down')
CUF = ControlSequence(lambda n: CSI + str(n) + 'C', 'Cursor Forward')
CUB = ControlSequence(lambda n: CSI + str(n) + 'D', 'Cursor Back')

CNL = ControlSequence(lambda n: CSI + str(n) + 'E', 'Cursor Next Line')
CPL = ControlSequence(lambda n: CSI + str(n) + 'F', 'Cursor Previous Line')
CHA = ControlSequence(lambda n: CSI + str(n) + 'G', 'Cursor Horizontal Line Absolute')

CUP = ControlSequence(lambda n, m: CSI + str(n) + ';' + str(m) + 'H', 'Cursor Position')
HVP = ControlSequence(lambda n, m: CSI + str(n) + ';' + str(m) + 'f', 'Horizontal Vertical Position')


def _str_val(val: ta.Any) -> str:
    if isinstance(val, enum.Enum):
        return str(val.value)
    else:
        return str(val)


class EDs(enum.Enum):
    FROM_CURSOR_TO_END = 0
    FROM_CURSOR_TO_BEGINNING = 1
    ALL = 2
    ALL_AND_SCROLLBACK = 3


ED = ControlSequence(lambda n: CSI + _str_val(n) + 'J', 'Erase in Display')


class ELs(enum.Enum):
    FROM_CURSOR_TO_END = 0
    FROM_CURSOR_TO_BEGINNING = 1
    ALL = 2


EL = ControlSequence(lambda n: CSI + _str_val(n) + 'K', 'Erase in Line')

SU = ControlSequence(lambda n: CSI + str(n) + 'S', 'Scroll Up')
SD = ControlSequence(lambda n: CSI + str(n) + 'T', 'Scroll Down')

DSR = ControlSequence(lambda: CSI + '6n', 'Device Status Report')

SCP = ControlSequence(lambda: CSI + 's', 'Save Cursor Position')
RCP = ControlSequence(lambda: CSI + 'u', 'Restore Cursor Position')

SHOW_CURSOR = ControlSequence(lambda: CSI + '?25h', 'Show Cursor')
HIDE_CURSOR = ControlSequence(lambda: CSI + '?25l', 'Hide Cursor')

SGR = ControlSequence(lambda n: CSI + _str_val(n) + 'm', 'Select Graphic Rendition')


class SGRs(lang.Namespace, lang.Final):
    RESET = 0
    NORMAL_COLOR_AND_INTENSITY = 22

    class FONT(enum.Enum):
        BOLD = 1
        FAINT = 2
        ITALIC = 3
        UNTERLINE = 4

        SLOW_BLINK = 5
        RAPID_BLINK = 6

        REVERSE_VIDEO = 7

        PRIMARY_FONT = 10
        ITALIC_OFF = 23
        UNDERLINE_OFF = 24
        BLINK_OFF = 25
        INVERSE_OFF = 27

        FRAMED = 51
        ENCIRCLED = 52
        OVERLINED = 53
        NOT_FRAMED_OR_ENCIRCLED = 54
        NOT_OVERLINED = 55

    class FG(enum.Enum):
        BLACK = 30
        RED = 31
        GREEN = 32
        YELLOW = 33
        BLUE = 34
        MAGENTA = 35
        CYAN = 36
        WHITE = 37

        BRIGHT_BLACK = 90
        BRIGHT_RED = 91
        BRIGHT_GREEN = 92
        BRIGHT_YELLOW = 93
        BRIGHT_BLUE = 94
        BRIGHT_MAGENTA = 95
        BRIGHT_CYAN = 96
        BRIGHT_WHITE = 97

    class BG(enum.Enum):
        BLACK = 40
        RED = 41
        GREEN = 42
        YELLOW = 43
        BLUE = 44
        MAGENTA = 45
        CYAN = 46
        WHITE = 47

        BRIGHT_BLACK = 100
        BRIGHT_RED = 101
        BRIGHT_GREEN = 102
        BRIGHT_YELLOW = 103
        BRIGHT_BLUE = 104
        BRIGHT_MAGENTA = 105
        BRIGHT_CYAN = 106
        BRIGHT_WHITE = 107


def _clamp_ofs(v: int, hi: int, ofs: int) -> str:
    if v < 0 or v > hi:
        raise ValueError(v)
    return str(v + ofs)


FG8 = ControlSequence(
    lambda n: CSI + '38;5;' + str(n) + 'm',
    '8-Bit Foreground Color')
FG8_STANDARD = ControlSequence(
    lambda n: CSI + '38;5;' + _clamp_ofs(n, 8, 0) + 'm',
    '8-Bit Foreground Color (Standard)')
FG8_HIGH_INTENSITY = ControlSequence(
    lambda n: CSI + '38;5;' + _clamp_ofs(n, 8, 8) + 'm',
    '8-Bit Foreground Color (High Intensity)')
FG8_216 = ControlSequence(
    lambda n: CSI + '38;5;' + _clamp_ofs(n, 216, 16) + 'm',
    '8-Bit Foreground Color (High Intensity)')
FG8_GRAYSCALE = ControlSequence(
    lambda n: CSI + '38;5;' + _clamp_ofs(n, 24, 232) + 'm',
    '8-Bit Foreground Color (Grayscale)')
FG8_RGB = ControlSequence(
    lambda r, g, b: CSI + '38;5;' + str(36 * r + 6 * g + b) + 'm',
    '8-Bit Foreground Color (RGB)')

BG8 = ControlSequence(
    lambda n: CSI + '48;5;' + str(n) + 'm',
    '8-Bit Background Color')
BG8_STANDARD = ControlSequence(
    lambda n: CSI + '48;5;' + _clamp_ofs(n, 8, 0) + 'm',
    '8-Bit Background Color (Standard)')
BG8_HIGH_INTENSITY = ControlSequence(
    lambda n: CSI + '48;5;' + _clamp_ofs(n, 8, 8) + 'm',
    '8-Bit Background Color (High Intensity)')
BG8_216 = ControlSequence(
    lambda n: CSI + '48;5;' + _clamp_ofs(n, 216, 16) + 'm',
    '8-Bit Background Color (High Intensity)')
BG8_GRAYSCALE = ControlSequence(
    lambda n: CSI + '48;5;' + _clamp_ofs(n, 24, 232) + 'm',
    '8-Bit Background Color (Grayscale)')
BG8_RGB = ControlSequence(
    lambda r, g, b: CSI + '48;5;' + str(36 * r + 6 * g + b) + 'm',
    '8-Bit Background Color (RGB)')

FG24_RGB = ControlSequence(
    lambda r, g, b: CSI + '38;2;' + str(r) + ';' + str(g) + ';' + str(b) + 'm',
    '24-Bit Foreground Color (RGB)')
BG24_RGB = ControlSequence(
    lambda r, g, b: CSI + '48;2;' + str(r) + ';' + str(g) + ';' + str(b) + 'm',
    '24-Bit Background Color (RGB)')

##


class ProgressBar:
    """
    TODO:
     - ProgressBarRenderer
     - right-justify
     - ProgressBarGroup
     - animate
    """

    def __init__(
            self,
            total: int | None = None,
            *,
            length: int = 40,
            interval: float = .2,
            start_time: float | None = None,
            out: ta.TextIO | None = None,
    ) -> None:
        super().__init__()

        self._total = total
        self._length = length
        self._interval = interval
        if start_time is None:
            start_time = time.time()
        self._start_time = start_time
        if out is None:
            out = sys.stdout
        self._out = out

        self._i = 0
        self._elapsed = 0.
        self._last_print = 0.

    def render(
            self,
            *,
            complete: bool = False,
    ) -> str:
        iter_per_sec = self._i / self._elapsed if self._elapsed > 0 else 0

        if self._total is not None:
            remaining = (self._total - self._i) / iter_per_sec if iter_per_sec > 0 else 0
            done = int(self._length * self._i / self._total)

            bar = f'[{"█" * done}{"." * (self._length - done)}]'
            info_parts = [
                f'{self._i}/{self._total}',
                f'{iter_per_sec:.2f} it/s',
                f'{self._elapsed:.2f}s elapsed',
                f'{remaining:.2f}s left',
            ]

        else:
            bar = f'[{("█" if complete else "?") * self._length}]'
            info_parts = [
                f'{self._i}',
                f'{iter_per_sec:.2f} it/s',
                f'{self._elapsed:.2f}s elapsed',
            ]

        info = ' | '.join(info_parts)
        return f'{bar} {info}'

    def print(
            self,
            *,
            now: float | None = None,
            **kwargs: ta.Any,
    ) -> None:
        if now is None:
            now = time.time()

        line = self.render(**kwargs)
        self._out.write(f'\033[2K\033[G{line}')
        self._out.flush()

        self._last_print = now

    def update(
            self,
            n: int = 1,
            *,
            now: float | None = None,
            silent: bool = False,
    ) -> None:
        if now is None:
            now = time.time()

        self._i += n
        self._elapsed = now - self._start_time

        if not silent:
            if now - self._last_print >= self._interval:
                self.print(now=now)


def progress_bar(
        seq: ta.Iterable[T],
        *,
        no_tty_check: bool = False,
        total: int | None = None,
        out: ta.TextIO | None = None,
        **kwargs: ta.Any,
) -> ta.Generator[T, None, None]:
    if out is None:
        out = sys.stdout

    if not no_tty_check and not out.isatty():
        yield from seq
        return

    if total is None:
        if isinstance(seq, ta.Sized):
            total = len(seq)

    pb = ProgressBar(
        total=total,
        out=out,
        **kwargs,
    )

    for item in seq:
        pb.update()
        yield item

    pb.print(complete=True)
    out.write('\n')


##


def main() -> None:
    import sys

    sys.stdout.write(SGR(SGRs.RESET))
    sys.stdout.write(BG8(15) + ' ')
    for i in range(20):
        sys.stdout.write(BG8(i) + ' ')
    sys.stdout.write('\n')
    for i in range(256):
        if i % 12 == 0:
            sys.stdout.write('\n')
        sys.stdout.write(BG8(i + 16) + ' ')
    sys.stdout.write(SGR(SGRs.RESET) + '\n')


if __name__ == '__main__':
    main()
