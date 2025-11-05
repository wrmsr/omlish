import functools
import re
import typing as ta
import unicodedata

from .types import CharBuffer
from .types import CharWidths


##


ANSI_ESCAPE_SEQUENCE = re.compile(r'\x1b\[[ -@]*[A-~]')


##


@functools.cache
def str_width(c: str) -> int:
    if ord(c) < 128:
        return 1
    w = unicodedata.east_asian_width(c)
    if w in ('N', 'Na', 'H', 'A'):
        return 1
    return 2


def wlen(s: str) -> int:
    if len(s) == 1 and s != '\x1a':
        return str_width(s)
    length = sum(str_width(i) for i in s)
    # remove lengths of any escape sequences
    sequence = ANSI_ESCAPE_SEQUENCE.findall(s)
    ctrl_z_cnt = s.count('\x1a')
    return length - sum(len(i) for i in sequence) + ctrl_z_cnt


##


ZERO_WIDTH_BRACKET = re.compile(r'\x01.*?\x02')
ZERO_WIDTH_TRANS = str.maketrans({'\x01': '', '\x02': ''})


def unbracket(s: str, including_content: bool = False) -> str:
    r"""
    Return `s` with \001 and \002 characters removed.

    If `including_content` is True, content between \001 and \002 is also stripped.
    """

    if including_content:
        return ZERO_WIDTH_BRACKET.sub('', s)
    return s.translate(ZERO_WIDTH_TRANS)


##


class Span(ta.NamedTuple):
    """Span indexing that's inclusive on both ends."""

    start: int
    end: int

    @classmethod
    def from_re(cls, m: ta.Match[str], group: int | str) -> ta.Self:
        re_span = m.span(group)
        return cls(re_span[0], re_span[1] - 1)


class ColorSpan(ta.NamedTuple):
    span: Span
    tag: str


##


class ColorCodes(ta.Protocol):
    def __getitem__(self, tag: str) -> str: ...

    @property
    def reset(self) -> str: ...


class NoColorCodes:
    def __getitem__(self, tag: str) -> str:
        return ''

    @property
    def reset(self) -> str:
        return ''


class AnsiColorCodes:
    CODES: ta.ClassVar[ta.Mapping[str, str]] = {
        'prompt': '\x1b[1;35m',
    }

    def __getitem__(self, tag: str) -> str:
        return self.CODES.get(tag, '')

    @property
    def reset(self) -> str:
        return '\x1b[0m'


def color_codes() -> ColorCodes:
    # return NoColorCodes()
    return AnsiColorCodes()


##


def disp_str(
        buffer: str,
        colors: list[ColorSpan] | None = None,
        start_index: int = 0,
        color_codes: ColorCodes = NoColorCodes(),
) -> tuple[CharBuffer, CharWidths]:
    r"""
    Decompose the input buffer into a printable variant with applied colors.

    Returns a tuple of two lists:
    - the first list is the input buffer, character by character, with color escape codes added (while those codes
      contain multiple ASCII characters, each code is considered atomic *and is attached for the corresponding visible
      character*);
    - the second list is the visible width of each character in the input buffer.

    Note on colors:
    - The `colors` list, if provided, is partially consumed within. We're using a list and not a generator since we need
      to hold onto the current unfinished span between calls to disp_str in case of multiline strings.
    - The `colors` list is computed from the start of the input block. `buffer` is only a subset of that input block, a
      single line within. This is why we need `start_index` to inform us which position is the start of `buffer`
      actually within user input. This allows us to match color spans correctly.

    Examples:
    >>> utils.disp_str("a = 9")
    (['a', ' ', '=', ' ', '9'], [1, 1, 1, 1, 1])

    >>> line = "while 1:"
    >>> colors = list(utils.gen_colors(line))
    >>> utils.disp_str(line, colors=colors)
    (['\x1b[1;34mw', 'h', 'i', 'l', 'e\x1b[0m', ' ', '1', ':'], [1, 1, 1, 1, 1, 1, 1, 1])

    """
    chars: CharBuffer = []
    char_widths: CharWidths = []

    if not buffer:
        return chars, char_widths

    while colors and colors[0].span.end < start_index:
        # move past irrelevant spans
        colors.pop(0)

    pre_color = ''
    post_color = ''
    if colors and colors[0].span.start < start_index:
        # looks like we're continuing a previous color (e.g. a multiline str)
        pre_color = color_codes[colors[0].tag]

    for i, c in enumerate(buffer, start_index):
        if colors and colors[0].span.start == i:  # new color starts now
            pre_color = color_codes[colors[0].tag]

        if c == '\x1a':  # CTRL-Z on Windows
            chars.append(c)
            char_widths.append(2)

        elif ord(c) < 128:
            chars.append(c)
            char_widths.append(1)

        elif unicodedata.category(c).startswith('C'):
            c = fr'\u{ord(c):04x}'
            chars.append(c)
            char_widths.append(len(c))

        else:
            chars.append(c)
            char_widths.append(str_width(c))

        if colors and colors[0].span.end == i:  # current color ends now
            post_color = color_codes.reset
            colors.pop(0)

        chars[-1] = pre_color + chars[-1] + post_color
        pre_color = ''
        post_color = ''

    if colors and colors[0].span.start < i and colors[0].span.end > i:
        # Even though the current color should be continued, reset it for now. The next call to `disp_str()` will revive
        # it.
        chars[-1] += color_codes.reset

    return chars, char_widths
