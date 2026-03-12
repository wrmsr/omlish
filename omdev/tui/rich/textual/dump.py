# @omlish-llm-author "opus-4.6"
from mpmath import arg

from .themes import DumpedTextualTheme
from .themes import render_dumped_textual_theme_src


##


def dump_textual_theme(name: str = 'textual-dark') -> DumpedTextualTheme:
    """
    Extract resolved design-variables *and* pre-blended colors from a built-in Textual theme.

    **Requires textual to be installed** -- only call this at dev time.

    Returns ``DumpedTextualTheme``.
    """

    # Late import so the rest of this module never touches textual
    from textual.color import Color  # noqa
    from textual.theme import BUILTIN_THEMES  # noqa

    theme = BUILTIN_THEMES[name]
    cs = theme.to_color_system()
    colors = cs.generate()

    # compute blended colors
    #
    # Several Textual markdown CSS rules use "<color> <percent>" notation, which means "that color at <percent> opacity
    # composited over the widget background". Rich's terminal styles don't support alpha, so we pre-blend them against
    # the theme's background.
    #
    # The blend formula is: `result = bg * (1 - factor) + fg * factor`. For $boost (which already *is* an RGBA hex), we
    # composite it on bg.
    #
    # Which rules need blending (hardcoded from _markdown.py DEFAULT_CSS):
    #
    #   MarkdownBlock &:dark > .code_inline
    #       background: $warning  10%       ->  code_inline_bg
    #       color:      $text-warning 95%   ->  code_inline_fg
    #
    #   MarkdownFence
    #       color:      rgb(210,210,210)    ->  code_block_fg  (literal, no blend)
    #       background: black 10%           ->  code_block_bg
    #
    #   MarkdownBlockQuote
    #       background: $boost              ->  block_quote_bg  (RGBA composite)
    #       border-left: outer $text-primary 50%  ->  block_quote_border
    #
    #   MarkdownH6 (uses $foreground-muted which is an RGBA hex)
    #       color:      $foreground-muted   ->  h6_color

    bg = Color.parse(colors['background'])

    def blend(color_key_or_hex: str, factor: float) -> str:
        """Blend a color at *factor* opacity over the theme background."""

        raw = colors.get(color_key_or_hex, color_key_or_hex)
        return bg.blend(Color.parse(raw), factor, alpha=1.0).hex

    def composite_rgba(rgba_hex: str) -> str:
        """Composite an RGBA hex (e.g. #FFFFFF0A) over the background."""

        c = Color.parse(rgba_hex)
        return (bg + c).hex

    is_dark = theme.dark

    blended: dict[str, str] = {}

    # inline code
    if is_dark:
        # &:dark > .code_inline { background: $warning 10%; color: $text-warning 95%; }
        blended['code_inline_bg'] = blend('warning', 0.10)
        blended['code_inline_fg'] = blend('text-warning', 0.95)
    else:
        # &:light > .code_inline { background: $error 5%; color: $text-error 95%; }
        blended['code_inline_bg'] = blend('error', 0.05)
        blended['code_inline_fg'] = blend('text-error', 0.95)

    # code fence
    blended['code_block_fg'] = '#D2D2D2'  # literal rgb(210,210,210) in CSS
    if is_dark:
        # background: black 10%;
        blended['code_block_bg'] = blend('#000000', 0.10)
    else:
        # &:light { background: white 30%; }
        blended['code_block_bg'] = blend('#FFFFFF', 0.30)

    # block quote
    # background: $boost;  ($boost is already RGBA from ColorSystem)
    blended['block_quote_bg'] = composite_rgba(colors['boost'])
    # border-left: outer $text-primary 50%;  (dark) / $text-secondary (light)
    if is_dark:
        blended['block_quote_border'] = blend('text-primary', 0.50)
    else:
        blended['block_quote_border'] = colors['text-secondary']

    # H6 foreground
    # $foreground-muted is usually an RGBA hex like #E0E0E099
    fm = colors['foreground-muted']
    if len(fm) == 9 and fm.startswith('#'):
        # RGBA -- extract alpha and blend
        alpha = int(fm[7:9], 16) / 255
        blended['h6_color'] = blend(fm[:7], alpha)
    else:
        blended['h6_color'] = fm

    ##
    # Pygments highlight styles
    #
    # Textual does NOT use Rich/Pygments for code block highlighting. It has its own pipeline
    # (textual.highlight.HighlightTheme) that maps Pygments token types to Textual-format style strings referencing
    # design-system variables like "$text-accent", "$text-success 90%", etc.
    #
    # We resolve those variable references and alpha-blend percentages against the *fence* background (the actual
    # surface code appears on) to produce concrete Pygments-format style strings that can be used with Rich's Syntax
    # renderer.
    #
    # Note: Token.String IS Token.Literal.String and Token.Number IS Token.Literal.Number in Pygments (they're
    # aliases). When both appear as keys in the STYLES dict, the later entry wins.

    from textual.highlight import HighlightTheme  # noqa

    fence_bg = Color.parse(blended['code_block_bg'])

    text_attrs = frozenset({'bold', 'italic', 'underline', 'strike'})

    def resolve_highlight_var(var_name: str, pct: float | None) -> str:
        """Resolve a $variable reference (with optional NN% alpha) to a hex color, blending against the fence bg."""

        raw = colors.get(var_name, var_name)

        # Handle "auto NN%" (e.g. $text -> "auto 87%")
        if raw.startswith('auto'):
            base = Color.parse('#FFFFFF') if is_dark else Color.parse('#000000')
            parts = raw.split()
            if len(parts) > 1 and parts[1].endswith('%'):
                var_alpha = int(parts[1][:-1]) / 100
            else:
                var_alpha = 1.0
            # Explicit pct in the style string overrides the variable's own alpha
            final_alpha = pct if pct is not None else var_alpha
            return fence_bg.blend(base, final_alpha, alpha=1.0).hex

        c = Color.parse(raw)
        if pct is not None:
            return fence_bg.blend(Color(c.r, c.g, c.b), pct, alpha=1.0).hex
        if c.a < 1.0:
            return fence_bg.blend(Color(c.r, c.g, c.b), c.a, alpha=1.0).hex
        return c.hex

    pygments_styles: dict[str, str] = {}

    # Base text: highlight() calls .stylize_before("$text"), making $text the default for all tokens
    pygments_styles['Token'] = resolve_highlight_var('text', None)

    for token_type, style_str in HighlightTheme.STYLES.items():
        token_key = str(token_type)

        if not style_str:
            pygments_styles[token_key] = ''
            continue

        parts = style_str.split()
        fg: str | None = None
        bg_col: str | None = None
        attrs: list[str] = []

        in_bg = False
        i = 0
        while i < len(parts):
            p = parts[i]

            if p == 'on':
                in_bg = True
                i += 1
                continue

            if p in text_attrs:
                attrs.append(p)
                i += 1
                continue

            if p.startswith('$'):
                var_name = p[1:]
                pct_val: float | None = None
                if (
                        i + 1 < len(parts)
                        and parts[i + 1].endswith('%')
                        and parts[i + 1][:-1].isdigit()
                ):
                    pct_val = int(parts[i + 1][:-1]) / 100
                    i += 1

                resolved = resolve_highlight_var(var_name, pct_val)
                if in_bg:
                    bg_col = resolved
                else:
                    fg = resolved
                i += 1
                continue

            i += 1

        # Build Pygments-format style string: "bold italic #RRGGBB bg:#RRGGBB"
        pygments_parts: list[str] = []
        pygments_parts.extend(attrs)
        if fg:
            pygments_parts.append(fg)
        if bg_col:
            pygments_parts.append(f'bg:{bg_col}')

        pygments_styles[token_key] = ' '.join(pygments_parts)

    return DumpedTextualTheme(
        name,
        colors=colors,
        blended=blended,
        pygments_styles=pygments_styles,
    )


###


def _main() -> None:
    import argparse  # noqa

    parser = arg.ArgumentParser()
    parser.add_argument('name', nargs='?', default='textual-dark')

    args = parser.parse_args()

    theme = dump_textual_theme(args.name)
    print(render_dumped_textual_theme_src(theme).strip())


if __name__ == '__main__':
    _main()
