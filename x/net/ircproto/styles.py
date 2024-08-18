import enum
import re
import typing as ta


class IrcTextColor(enum.Enum):
    WHITE = 0
    BLACK = 1
    NAVY = 2
    GREEN = 3
    RED = 4
    MAROON = 5
    PURPLE = 6
    OLIVE = 7
    YELLOW = 8
    LIGHTGREEN = 9
    TEAL = 10
    CYAN = 11
    ROYALBLUE = 12
    MAGENTA = 13
    GRAY = 14
    LIGHTGRAY = 15


class IrcTextStyle(enum.Enum):
    BOLD = '\x02'
    ITALIC = '\x1d'
    UNDERLINE = '\x1f'
    REVERSE = '\x16'
    PLAIN = '\x0f'


STYLES_RE = re.compile(b'(\x03\\d+(?:,\\d+)?)|[\x02\x03\x1d\x1f\x16\x0f]')


def styled(
        text: str,
        foreground: IrcTextColor | None = None,
        background: IrcTextColor | None = None,
        styles: ta.Iterable[IrcTextStyle] | None = None,
) -> str:
    """Apply mIRC compatible colors and styles to the given text."""

    # Apply coloring
    if foreground and not background:
        text = '\x03%d%s\x03' % (foreground.value, text)
    elif foreground and background:
        text = '\x03%d,%d%s\x03' % (foreground.value, background.value, text)

    # Apply text styles
    if styles:
        if isinstance(styles, IrcTextStyle):
            text = styles.value + text
        else:
            text = ''.join(style.value for style in styles) + text

        text += IrcTextStyle.plain.value  # reset to default at the end

    return text


def strip_styles(text: str) -> str:
    """Remove all mIRC compatible styles and coloring from the given text."""

    return STYLES_RE.sub('', text)
