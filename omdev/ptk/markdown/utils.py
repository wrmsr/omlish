import enum
import typing as ta

from pygments.lexers import get_lexer_by_name
from pygments.util import ClassNotFound

from ... import ptk
from .border import Border
from .border import SquareBorder


##


class FormattedTextAlign(enum.Enum):
    """Alignment of formatted text."""

    LEFT = 'LEFT'
    RIGHT = 'RIGHT'
    CENTER = 'CENTER'


def last_line_length(ft: ptk.StyleAndTextTuples) -> int:
    """Calculate the length of the last line in formatted text."""

    line: ptk.StyleAndTextTuples = []
    for style, text, *_ in ft[::-1]:
        index = text.find('\n')
        line.append((style, text[index + 1:]))
        if index > -1:
            break

    return ptk.fragment_list_width(line)


def max_line_width(ft: ptk.StyleAndTextTuples) -> int:
    """Calculate the length of the longest line in formatted text."""

    return max(ptk.fragment_list_width(line) for line in ptk.split_lines(ft))


def fragment_list_to_words(fragments: ptk.StyleAndTextTuples) -> ta.Iterable[ptk.OneStyleAndTextTuple]:
    """Split formatted text into word fragments."""

    for style, string, *mouse_handler in fragments:
        parts = string.split(' ')
        for part in parts[:-1]:
            yield ta.cast('ptk.OneStyleAndTextTuple', (style, part, *mouse_handler))
            yield ta.cast('ptk.OneStyleAndTextTuple', (style, ' ', *mouse_handler))

        yield ta.cast('ptk.OneStyleAndTextTuple', (style, parts[-1], *mouse_handler))


def apply_style(ft: ptk.StyleAndTextTuples, style: str) -> ptk.StyleAndTextTuples:
    """Apply a style to formatted text."""

    return [
        (
            f'{fragment_style} {style}'
            if '[ZeroWidthEscape]' not in fragment_style else fragment_style,
            text,
        )
        for (fragment_style, text, *_) in ft
    ]


def strip(
    ft: ptk.StyleAndTextTuples,
    left: bool = True,
    right: bool = True,
    char: str | None = None,
) -> ptk.StyleAndTextTuples:
    """
    Strip whitespace (or a given character) from the ends of formatted text.

    Args:
        ft: The formatted text to strip
        left: If :py:const:`True`, strip from the left side of the input
        right: If :py:const:`True`, strip from the right side of the input
        char: The character to strip. If :py:const:`None`, strips whitespace
    Returns:
        The stripped formatted text
    """

    result = ft[:]
    for toggle, index, strip_func in [
        (left, 0, str.lstrip),
        (right, -1, str.rstrip),
    ]:
        if result and toggle:
            text = strip_func(result[index][1], char)

            while result and not text:
                del result[index]
                if not result:
                    break

                text = strip_func(result[index][1], char)

            if result and '[ZeroWidthEscape]' not in result[index][0]:
                result[index] = (result[index][0], text)

    return result


def truncate(
    ft: ptk.StyleAndTextTuples,
    width: int,
    style: str = '',
    placeholder: str = '…',
) -> ptk.StyleAndTextTuples:
    """
    Truncates all lines at a given length.

    Args:
        ft: The formatted text to truncate
        width: The width at which to truncate the text
        style: The style to apply to the truncation placeholder. The style of the truncated text will be used if not
            provided
        placeholder: The string that will appear at the end of a truncated line
    Returns:
        The truncated formatted text
    """

    result: ptk.StyleAndTextTuples = []
    phw = sum(ptk.get_cwidth(c) for c in placeholder)
    for line in ptk.split_lines(ft):
        used_width = 0
        for item in line:
            fragment_width = sum(
                ptk.get_cwidth(c)
                for c in item[1]
                if '[ZeroWidthEscape]' not in item[0]
            )

            if used_width + fragment_width > width - phw:
                remaining_width = width - used_width - fragment_width - phw
                result.append((item[0], item[1][:remaining_width]))
                result.append((style or item[0], placeholder))
                break

            result.append(item)
            used_width += fragment_width

        result.append(('', '\n'))

    result.pop()
    return result


def wrap(
    ft: ptk.StyleAndTextTuples,
    width: int,
    style: str = '',
    placeholder: str = '…',
) -> ptk.StyleAndTextTuples:
    """
    Wraps formatted text at a given width. If words are longer than the given line they will be truncated

    Args:
        ft: The formatted text to wrap
        width: The width at which to wrap the text
        style: The style to apply to the truncation placeholder
        placeholder: The string that will appear at the end of a truncated line
    Returns:
        The wrapped formatted text
    """

    result: ptk.StyleAndTextTuples = []
    lines = list(ptk.split_lines(ft))
    for i, line in enumerate(lines):
        if ptk.fragment_list_width(line) <= width:
            result += line
            if i < len(lines) - 1:
                result.append(('', '\n'))
            continue

        used_width = 0
        for item in fragment_list_to_words(line):
            fragment_width = sum(
                ptk.get_cwidth(c)
                for c in item[1]
                if '[ZeroWidthEscape]' not in item[0]
            )

            # Start a new line we are at the end
            if used_width + fragment_width > width and used_width > 0:
                # Remove trailing whitespace
                result = strip(result, left=False)
                result.append(('', '\n'))
                used_width = 0

            # Truncate words longer than a line
            if fragment_width > width and used_width == 0:
                result += truncate([item], width, style, placeholder)
                used_width += fragment_width

            # Left-strip words at the start of a line
            elif used_width == 0:
                result += strip([item], right=False)
                used_width += fragment_width

            # Otherwise just add the word to the line
            else:
                result.append(item)
                used_width += fragment_width

    return result


def align(
    how: FormattedTextAlign,
    ft: ptk.StyleAndTextTuples,
    width: int | None = None,
    style: str = '',
    placeholder: str = '…',
) -> ptk.StyleAndTextTuples:
    """
    Align formatted text at a given width.

    Args:
        how: The alignment direction
        ft: The formatted text to strip
        width: The width to which the output should be padded. If :py:const:`None`, the length of the longest line is
            used
        style: The style to apply to the padding
        placeholder: The string that will appear at the end of a truncated line
    Returns:
        The aligned formatted text
    """

    lines = ptk.split_lines(ft)
    if width is None:
        lines = [strip(line) for line in ptk.split_lines(ft)]
        width = max(ptk.fragment_list_width(line) for line in lines)

    result: ptk.StyleAndTextTuples = []
    for line in lines:
        line_width = ptk.fragment_list_width(line)

        # Truncate the line if it is too long
        if line_width > width:
            result += truncate(line, width, style, placeholder)

        else:
            pad_left = pad_right = 0

            if how == FormattedTextAlign.CENTER:
                pad_left = (width - line_width) // 2
                pad_right = width - line_width - pad_left

            elif how == FormattedTextAlign.LEFT:
                pad_right = width - line_width

            elif how == FormattedTextAlign.RIGHT:
                pad_left = width - line_width

            if pad_left:
                result.append((style, ' ' * pad_left))

            result += line

            if pad_right:
                result.append((style, ' ' * pad_right))

        result.append((style, '\n'))

    result.pop()
    return result


def indent(
    ft: ptk.StyleAndTextTuples,
    margin: str = ' ',
    style: str = '',
    skip_first: bool = False,
) -> ptk.StyleAndTextTuples:
    """
    Indents formatted text with a given margin.

    Args:
        ft: The formatted text to strip
        margin: The margin string to add
        style: The style to apply to the margin
        skip_first: If :py:const:`True`, the first line is skipped
    Returns:
        The indented formatted text
    """

    result: ptk.StyleAndTextTuples = []
    for i, line in enumerate(ptk.split_lines(ft)):
        if not (i == 0 and skip_first):
            result.append((style, margin))
        result += line
        result.append(('', '\n'))

    result.pop()
    return result


def add_border(
    ft: ptk.StyleAndTextTuples,
    width: int | None = None,
    style: str = '',
    border: type[Border] = SquareBorder,
) -> ptk.StyleAndTextTuples:
    """
    Adds a border around formatted text.

    Args:
        ft: The formatted text to enclose with a border
        width: The target width of the output including the border
        style: The style to apply to the border
        border: The border to apply
    Returns:
        The indented formatted text
    """

    # if border is None:
    # See mypy issue #4236
    # border = cast("Type[Border]", Border)
    if width is None:
        width = max_line_width(ft) + 4

    # ft = align(FormattedTextAlign.LEFT, ft, width - 4)
    result: ptk.StyleAndTextTuples = []

    result.append((
        style,
        border.TOP_LEFT + border.HORIZONTAL * (width - 2) + border.TOP_RIGHT + '\n',
    ))

    for line in ptk.split_lines(ft):
        result += [
            (style, border.VERTICAL),
            ('', ' '),
            *line,
            ('', ' '),
            (style, border.VERTICAL + '\n'),
        ]

    result.append((
        style,
        border.BOTTOM_LEFT + border.HORIZONTAL * (width - 2) + border.BOTTOM_RIGHT,
    ))

    return result


def lex(ft: ptk.StyleAndTextTuples, lexer_name: str) -> ptk.StyleAndTextTuples:
    """Format formatted text using a named :py:mod:`pygments` lexer."""

    from prompt_toolkit.lexers.pygments import _token_cache  # noqa

    text = ptk.fragment_list_to_text(ft)

    try:
        lexer = get_lexer_by_name(lexer_name)
    except ClassNotFound:
        return ft
    else:
        return [
            (_token_cache[t], v)
            for _, t, v in lexer.get_tokens_unprocessed(text)
        ]
