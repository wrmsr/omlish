import typing as ta

from ... import ptk
from .border import DoubleBorder
from .border import SquareBorder
from .utils import FormattedTextAlign
from .utils import add_border
from .utils import align
from .utils import apply_style
from .utils import indent
from .utils import lex
from .utils import strip
from .utils import wrap


if ta.TYPE_CHECKING:
    from markdown_it.token import Token


TagRule: ta.TypeAlias = ta.Callable[
    [
        ptk.StyleAndTextTuples,
        int,
        int,
        'Token',
    ],
    ptk.StyleAndTextTuples,
]


##


def h1(
        ft: ptk.StyleAndTextTuples,
        width: int,
        left: int,
        token: 'Token',
) -> ptk.StyleAndTextTuples:
    """Format a top-level heading wrapped and centered with a full width double border."""

    ft = wrap(ft, width - 4)
    ft = align(FormattedTextAlign.CENTER, ft, width=width - 4)
    ft = add_border(ft, width, style='class:md.h1.border', border=DoubleBorder)
    ft.append(('', '\n\n'))
    return ft


def h2(
        ft: ptk.StyleAndTextTuples,
        width: int,
        left: int,
        token: 'Token',
) -> ptk.StyleAndTextTuples:
    """Format a 2nd-level headding wrapped and centered with a double border."""

    ft = wrap(ft, width=width - 4)
    ft = align(FormattedTextAlign.CENTER, ft)
    ft = add_border(ft, style='class:md.h2.border', border=SquareBorder)
    ft = align(FormattedTextAlign.CENTER, ft, width=width)
    ft.append(('', '\n\n'))
    return ft


def h(
        ft: ptk.StyleAndTextTuples,
        width: int,
        left: int,
        token: 'Token',
) -> ptk.StyleAndTextTuples:
    """Format headings wrapped and centeredr."""

    ft = wrap(ft, width)
    ft = align(FormattedTextAlign.CENTER, ft, width=width)
    ft.append(('', '\n\n'))
    return ft


def p(
        ft: ptk.StyleAndTextTuples,
        width: int,
        left: int,
        token: 'Token',
) -> ptk.StyleAndTextTuples:
    """Format paragraphs wrapped."""

    ft = wrap(ft, width)
    ft.append(('', '\n' if token.hidden else '\n\n'))
    return ft


def ul(
        ft: ptk.StyleAndTextTuples,
        width: int,
        left: int,
        token: 'Token',
) -> ptk.StyleAndTextTuples:
    """Format unordered lists."""

    ft.append(('', '\n'))
    return ft


def ol(
        ft: ptk.StyleAndTextTuples,
        width: int,
        left: int,
        token: 'Token',
) -> ptk.StyleAndTextTuples:
    """Formats ordered lists."""

    ft.append(('', '\n'))
    return ft


def li(
        ft: ptk.StyleAndTextTuples,
        width: int,
        left: int,
        token: 'Token',
) -> ptk.StyleAndTextTuples:
    """Formats list items."""

    ft = strip(ft)

    # Determine if this is an ordered or unordered list
    if token.attrs.get('data-list-type') == 'ol':
        margin_style = 'class:md.ol.margin'
    else:
        margin_style = 'class:md.ul.margin'

    # Get the margin (potentially contains aligned item numbers)
    margin = str(token.attrs.get('data-margin', '•'))

    # We put a speace each side of the margin
    ft = indent(ft, margin=' ' * (len(margin) + 2), style=margin_style)
    ft[0] = (ft[0][0], f' {margin} ')

    ft.append(('', '\n'))
    return ft


def hr(
        ft: ptk.StyleAndTextTuples,
        width: int,
        left: int,
        token: 'Token',
) -> ptk.StyleAndTextTuples:
    """Format horizontal rules."""

    ft = [
        ('class:md.hr', '─' * width),
        ('', '\n\n'),
    ]
    return ft


def br(
        ft: ptk.StyleAndTextTuples,
        width: int,
        left: int,
        token: 'Token',
) -> ptk.StyleAndTextTuples:
    """Format line breaks."""

    return [('', '\n')]


def blockquote(
        ft: ptk.StyleAndTextTuples,
        width: int,
        left: int,
        token: 'Token',
) -> ptk.StyleAndTextTuples:
    """Format blockquotes with a solid left margin."""

    ft = strip(ft)
    ft = indent(ft, margin='▌ ', style='class:md.blockquote.margin')
    ft.append(('', '\n\n'))
    return ft


def code(
        ft: ptk.StyleAndTextTuples,
        width: int,
        left: int,
        token: 'Token',
) -> ptk.StyleAndTextTuples:
    """Format inline code, and lexes and formats code blocks with a border."""

    if token.block:
        ft = strip(ft, left=False, right=True, char='\n')
        ft = lex(ft, lexer_name=token.info)
        ft = align(FormattedTextAlign.LEFT, ft, width - 4)
        ft = add_border(ft, width, style='class:md.code.border', border=SquareBorder)
        ft.append(('', '\n\n'))
    else:
        ft = apply_style(ft, style='class:md.code.inline')

    return ft


def math(
        ft: ptk.StyleAndTextTuples,
        width: int,
        left: int,
        token: 'Token',
) -> ptk.StyleAndTextTuples:
    """Format inline maths, and quotes math blocks."""

    if token.block:
        return blockquote(ft, width - 2, left, token)
    else:
        return ft


def a(
        ft: ptk.StyleAndTextTuples,
        width: int,
        left: int,
        token: 'Token',
) -> ptk.StyleAndTextTuples:
    """Format hyperlinks and adds link escape sequences."""

    result: ptk.StyleAndTextTuples = []
    href = token.attrs.get('href')
    if href:
        result.append(('[ZeroWidthEscape]', f'\x1b]8;;{href}\x1b\\'))
    result += ft
    if href:
        result.append(('[ZeroWidthEscape]', '\x1b]8;;\x1b\\'))
    return result


def img(
        ft: ptk.StyleAndTextTuples,
        width: int,
        left: int,
        token: 'Token',
) -> ptk.StyleAndTextTuples:
    """Format image titles."""

    bounds = ('', '')
    if not ptk.to_plain_text(ft):
        # Add fallback text if there is no image title
        title = str(token.attrs.get('alt'))

        # Try getting the filename
        src = str(token.attrs.get('src', ''))
        if not title and not src.startswith('data:'):
            title = src.rsplit('/', 1)[-1]
        if not title:
            title = 'Image'
        ft = [('class:md.img', title)]

    # Add the sunrise emoji to represent an image. I would use :framed_picture:, but it requires multiple code-points
    # and causes breakage in many terminals
    result = [('class:md.img', '🌄 '), *ft]
    result = apply_style(result, style='class:md.img')
    result = [
        ('class:md.img.border', f'{bounds[0]}'),
        *result,
        ('class:md.img.border', f'{bounds[1]}'),
    ]
    return result


##


# Maps HTML tag names to formatting functions. Functionality can be extended by modifying this dictionary
TAG_RULES: ta.Mapping[str, TagRule] = {
    'h1': h1,
    'h2': h2,
    'h3': h,
    'h4': h,
    'h5': h,
    'h6': h,
    'p': p,
    'ul': ul,
    'ol': ol,
    'li': li,
    'hr': hr,
    'br': br,
    'blockquote': blockquote,
    'code': code,
    'math': math,
    'a': a,
    'img': img,
}


# Mapping showing how much width the formatting of block elements used. This is used to reduce the available width when
# rendering child elements
TAG_INSETS = {
    'li': 3,
    'blockquote': 2,
}
