# @omlish-llm-author "opus-4.6"
import dataclasses as dc
import io
import typing as ta


if ta.TYPE_CHECKING:
    from pygments.style import Style as PygmentsStyle
    from rich.syntax import PygmentsSyntaxTheme
    from rich.themes import Theme


##


@dc.dataclass(frozen=True)
class DumpedTextualTheme:
    name: str

    _: dc.KW_ONLY

    colors: ta.Mapping[str, str]
    blended: ta.Mapping[str, str]

    # Pygments token type string -> pygments-format style string (e.g. "bold #FFC473 bg:#101010"). Resolved from
    # textual.highlight.HighlightTheme.STYLES with all $variable references and alpha-blending computed against the
    # fence (code block) background. These are language-agnostic -- Pygments token types are shared across all lexers.
    pygments_styles: ta.Mapping[str, str] | None = None


##


def render_dumped_textual_theme_src(dtx_theme: DumpedTextualTheme) -> str:
    out = io.StringIO()
    tag = dtx_theme.name.upper().replace('-', '_')

    out.write(f'# Dumped from Textual theme {dtx_theme.name!r}\n')
    out.write(f'TEXTUAL_{tag} = DumpedTextualTheme(\n')
    out.write(f'    {dtx_theme.name!r},\n')

    out.write('\n')
    out.write('    colors={\n')
    for k, v in dtx_theme.colors.items():
        out.write(f'        {k!r}: {v!r},\n')
    out.write('    },\n')

    out.write('\n')
    out.write('    blended={\n')
    for k, v in dtx_theme.blended.items():
        out.write(f'        {k!r}: {v!r},\n')
    out.write('    },\n')

    if dtx_theme.pygments_styles is not None:
        out.write('\n')
        out.write('    pygments_styles={\n')
        for k, v in dtx_theme.pygments_styles.items():
            out.write(f'        {k!r}: {v!r},\n')
        out.write('    },\n')

    out.write(')\n')
    return out.getvalue()


##


def _parse_text_style(spec: str) -> dict[str, ta.Any]:
    """Turn a textual text-style string like "bold underline" into keyword args suitable for ``rich.style.Style()``."""

    mapping = {
        'bold': 'bold',
        'italic': 'italic',
        'underline': 'underline',
        'strike': 'strike',
        'reverse': 'reverse',
        'dim': 'dim',
    }
    result: dict[str, bool] = {}
    for word in spec.split():
        if word in mapping:
            result[mapping[word]] = True
    return result


def build_theme(dtx_theme: DumpedTextualTheme) -> Theme:
    """
    Return a ``rich.theme.Theme`` whose ``markdown.*`` styles match what Textual's Markdown widget renders in its dark
    theme.

    The returned Theme inherits from Rich's built-in defaults so that non-markdown styles are unaffected.
    """

    from rich.style import Style  # noqa
    from rich.themes import Theme  # noqa

    c = dtx_theme.colors
    b = dtx_theme.blended

    styles: dict[str, Style] = {
        # headings
        'markdown.h1': Style(
            color=c['markdown-h1-color'],
            **_parse_text_style(c['markdown-h1-text-style']),
        ),
        'markdown.h1.border': Style(),  # Textual doesn't render a border rule for H1
        'markdown.h2': Style(
            color=c['markdown-h2-color'],
            **_parse_text_style(c['markdown-h2-text-style']),
        ),
        'markdown.h3': Style(
            color=c['markdown-h3-color'],
            **_parse_text_style(c['markdown-h3-text-style']),
        ),
        'markdown.h4': Style(
            color=c['markdown-h4-color'],
            **_parse_text_style(c['markdown-h4-text-style']),
        ),
        'markdown.h5': Style(
            color=c['markdown-h5-color'],
            **_parse_text_style(c['markdown-h5-text-style']),
        ),
        'markdown.h6': Style(
            color=b['h6_color'],
            **_parse_text_style(c['markdown-h6-text-style']),
        ),

        # inline styles
        'markdown.code': Style(
            color=b['code_inline_fg'],
            bgcolor=b['code_inline_bg'],
        ),
        'markdown.em': Style(italic=True),
        'markdown.emph': Style(italic=True),
        'markdown.strong': Style(bold=True),
        'markdown.s': Style(strike=True),

        # block-level elements
        'markdown.code_block': Style(
            color=b['code_block_fg'],
            bgcolor=b['code_block_bg'],
        ),
        'markdown.block_quote': Style(
            color=c.get('text-primary', c['foreground']),
            # Rich can't draw a left-border, but the color tint is the most visible part of the style.
        ),
        'markdown.paragraph': Style(),  # no special color, same as Textual

        'markdown.hr': Style(
            color=c['secondary'],
        ),

        # lists
        'markdown.item': Style(),
        'markdown.item.bullet': Style(
            color=c['text-primary'],
            bold=True,
        ),
        'markdown.item.number': Style(
            color=c['text-primary'],
        ),

        # tables
        'markdown.table.header': Style(
            color=c['primary'],
            bold=True,
        ),
        'markdown.table.border': Style(
            color=c['primary'],
        ),

        # links
        'markdown.link': Style(
            color=c['text-primary'],
            underline=True,
        ),
        'markdown.link_url': Style(
            color=c['primary'],
            underline=True,
        ),
    }

    return Theme(styles, inherit=True)


##


def build_pygments_style(dtx_theme: DumpedTextualTheme) -> type[PygmentsStyle]:
    """
    Build a Pygments ``Style`` subclass from dumped theme data that matches Textual's code block highlighting.

    **Does not import textual** -- works purely from the pre-resolved ``pygments_styles`` dict.

    The returned class can be passed to ``rich.syntax.PygmentsSyntaxTheme()`` or used directly with Pygments.
    """

    if (pygments_styles := dtx_theme.pygments_styles) is None:
        raise ValueError('No pygments_styles in theme')

    from pygments.style import Style as PygmentsStyle  # noqa
    from pygments.token import string_to_tokentype  # noqa

    token_styles = {
        string_to_tokentype(k): v
        for k, v in pygments_styles.items()
    }

    return type(  # noqa
        'TextualPygmentsStyle',
        (PygmentsStyle,),
        {
            'background_color': dtx_theme.blended.get('code_block_bg', ''),
            'styles': token_styles,
        },
    )


def build_pygments_theme(dtx_theme: DumpedTextualTheme) -> PygmentsSyntaxTheme:
    from rich.syntax import PygmentsSyntaxTheme  # noqa

    return PygmentsSyntaxTheme(build_pygments_style(dtx_theme))
