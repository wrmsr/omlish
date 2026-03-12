from .themes import DumpedTextualTheme


##


##
# Pre-computed color values for textual-dark (v8.1.1).
#
# These are the *resolved* hex values that Textual's ColorSystem.generate() produces for the default "textual-dark"
# theme. Only the subset that matters for markdown rendering is kept here.
#


TEXTUAL_DARK = DumpedTextualTheme(
    'textual-dark',

    colors={
        # Core palette
        'primary':           '#0178D4',
        'secondary':         '#004578',
        'foreground':        '#E0E0E0',
        'background':        '#121212',
        'warning':           '#FEA62B',
        'error':             '#B93C5B',
        'surface':           '#1E1E1E',

        # Derived text-on-background tints
        'text-primary':      '#57A5E2',
        'text-secondary':    '#5684A5',
        'text-warning':      '#FFC473',
        'text-error':        '#D17E92',

        # Foreground variants
        'foreground-muted':  '#E0E0E099',  # 60 % alpha

        # Markdown header variables (straight from design.py defaults)
        'markdown-h1-color':      '#0178D4',
        'markdown-h1-text-style': 'bold',
        'markdown-h2-color':      '#0178D4',
        'markdown-h2-text-style': 'underline',
        'markdown-h3-color':      '#0178D4',
        'markdown-h3-text-style': 'bold',
        'markdown-h4-color':      '#E0E0E0',
        'markdown-h4-text-style': 'bold underline',
        'markdown-h5-color':      '#E0E0E0',
        'markdown-h5-text-style': 'bold',
        'markdown-h6-color':      '#E0E0E099',
        'markdown-h6-text-style': 'bold',
    },

    blended={
        # Pre-blended colors for elements that use alpha/percentage notation in Textual CSS. Computed against
        # background #121212.

        # MarkdownBlock &:dark > .code_inline  ->  bg: $warning 10%, color: $text-warning 95%
        'code_inline_bg':     '#292014',
        'code_inline_fg':     '#F3BB6E',
        # MarkdownFence  ->  bg: black 10%  (over #121212)
        'code_block_bg':      '#101010',
        'code_block_fg':      '#D2D2D2',   # rgb(210,210,210) literal in textual CSS
        # MarkdownBlockQuote  ->  bg: $boost (white 4 %)
        'block_quote_bg':     '#1B1B1B',
        # MarkdownBlockQuote  ->  border-left: outer $text-primary 50%
        'block_quote_border': '#345B7A',
        # foreground-muted blended (for H6 -- 60 % alpha white-ish on #121212)
        'h6_color':           '#8D8D8D',
    },

    pygments_styles={
        # Resolved from textual.highlight.HighlightTheme.STYLES.
        # Alpha-blended against fence bg #101010. Base text from highlight()'s stylize_before("$text").
        'Token':                         '#DFDFDF',
        'Token.Comment':                 '#9F9F9F',
        'Token.Error':                   '#D17E92 bg:#441E27',
        'Token.Generic.Emph':            'italic',
        'Token.Generic.Error':           '#D17E92 bg:#441E27',
        'Token.Generic.Heading':         'underline #57A5E2',
        'Token.Generic.Strong':          'bold',
        'Token.Generic.Subheading':      '#57A5E2',
        'Token.Keyword':                 '#FFC473',
        'Token.Keyword.Constant':        'bold #71AC84',
        'Token.Keyword.Namespace':       '#D17E92',
        'Token.Keyword.Type':            'bold',
        'Token.Literal.Number':          '#FFC473',
        'Token.Literal.String':          '#8AD4A1',
        'Token.Literal.String.Backtick': '#9F9F9F',
        'Token.Literal.String.Doc':      'italic #71AC84',
        'Token.Literal.String.Double':   '#7DC092',
        'Token.Name':                    '#57A5E2',
        'Token.Name.Attribute':          '#FFC473',
        'Token.Name.Builtin':            '#FFC473',
        'Token.Name.Builtin.Pseudo':     'italic',
        'Token.Name.Class':              'bold #FFC473',
        'Token.Name.Constant':           '#D17E92',
        'Token.Name.Decorator':          'bold #57A5E2',
        'Token.Name.Function':           'underline #FFC473',
        'Token.Name.Function.Magic':     'underline #FFC473',
        'Token.Name.Tag':                'bold #57A5E2',
        'Token.Name.Variable':           '#5684A5',
        # Note: Token.Number IS Token.Literal.Number in Pygments (alias), so only the Literal.Number entry is needed.
        'Token.Operator':                'bold',
        'Token.Operator.Word':           'bold #D17E92',
        'Token.Whitespace':              '',
    },
)
