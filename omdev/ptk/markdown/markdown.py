"""
TODO:
 - accept pre-parsed tokens
 - provide live view in this pkg
"""
import itertools
import typing as ta

from ... import ptk
from .border import Border
from .border import SquareBorder
from .parser import markdown_parser
from .tags import TAG_INSETS
from .tags import TAG_RULES
from .utils import FormattedTextAlign
from .utils import align
from .utils import apply_style
from .utils import last_line_length
from .utils import lex
from .utils import strip
from .utils import wrap


if ta.TYPE_CHECKING:
    from markdown_it.token import Token


##


_SIDES = {
    'left': FormattedTextAlign.LEFT,
    'right': FormattedTextAlign.RIGHT,
    'center': FormattedTextAlign.CENTER,
}


class Markdown:
    """A markdown formatted text renderer. Accepts a markdown string and renders it at a given width."""

    def __init__(
            self,
            markup: str,
            *,
            width: int | None = None,
            strip_trailing_lines: bool = True,
    ) -> None:
        """
        Initialize the markdown formatter.

        Args:
            markup: The markdown text to render
            width: The width in characters available for rendering. If :py:const:`None` the terminal width will be used
            strip_trailing_lines: If :py:const:`True`, empty lines at the end of the rendered output will be removed
        """

        super().__init__()

        self.markup = markup
        self.width = width or ptk.get_app_session().output.get_size().columns
        self.strip_trailing_lines = strip_trailing_lines

        if (parser := markdown_parser()) is not None:
            self.formatted_text = self.render(
                tokens=parser.parse(self.markup),
                width=self.width,
            )
        else:
            self.formatted_text = lex(
                ptk.to_formatted_text(self.markup),
                lexer_name='markdown',
            )

        if strip_trailing_lines:
            self.formatted_text = strip(
                self.formatted_text,
                left=False,
                char='\n',
            )

    def render(
            self,
            tokens: ta.Sequence['Token'],
            width: int = 80,
            left: int = 0,
    ) -> ptk.StyleAndTextTuples:
        """
        Render a list of parsed markdown tokens.

        Args:
            tokens: The list of parsed tokens to render
            width: The width at which to render the tokens
            left: The position on the current line at which to render the output - used to indent subsequent lines when
                rendering inline blocks like images
        Returns:
            Formatted text
        """

        ft = []

        i = 0
        while i < len(tokens):
            token = tokens[i]

            # If this is an inline block, render it's children
            if token.type == 'inline' and token.children:
                ft += self.render(token.children, width)
                i += 1

            # Otherwise gather the tokens in the current block
            else:
                nest = 0
                tokens_in_block = 0
                for j, token in enumerate(tokens[i:]):
                    nest += token.nesting
                    if nest == 0:
                        tokens_in_block = j
                        break

                # If there is a special method for rendering the block, use it

                # Table require a lot of care
                if token.tag == 'table':
                    ft += self.render_table(
                        tokens[i:i + tokens_in_block + 1],
                        width=width,
                        left=last_line_length(ft),
                    )

                # We need to keep track of item numbers in ordered lists
                elif token.tag == 'ol':
                    ft += self.render_ordered_list(
                        tokens[i:i + tokens_in_block + 1],
                        width=width,
                        left=last_line_length(ft),
                    )

                # Otherwise all other blocks are rendered in the same way
                else:
                    ft += self.render_block(
                        tokens[i:i + tokens_in_block + 1],
                        width=width,
                        left=last_line_length(ft),
                    )

                i += j + 1

        return ft

    def render_block(
            self,
            tokens: ta.Sequence['Token'],
            width: int,
            left: int = 0,
    ) -> ptk.StyleAndTextTuples:
        """
        Render a list of parsed markdown tokens representing a block element.

        Args:
            tokens: The list of parsed tokens to render
            width: The width at which to render the tokens
            left: The position on the current line at which to render the output - used to indent subsequent lines when
                rendering inline blocks like images
        Returns:
            Formatted text
        """

        ft = []
        token = tokens[0]

        # Restrict width if necessary
        inset = TAG_INSETS.get(token.tag)
        if inset:
            width -= inset

        style = 'class:md'
        if token.tag:
            style = f'{style}.{token.tag}'

        # Render innards
        if len(tokens) > 1:
            ft += self.render(tokens[1:-1], width)
            ft = apply_style(ft, style)
        else:
            ft.append((style, token.content))

        # Apply tag rule
        rule = TAG_RULES.get(token.tag)
        if rule:
            ft = rule(
                ft,
                width,
                left,
                token,
            )

        return ft

    def render_ordered_list(
            self,
            tokens: ta.Sequence['Token'],
            width: int,
            left: int = 0,
    ) -> ptk.StyleAndTextTuples:
        """Render an ordered list by adding indices to the child list items."""

        # Find the list item tokens
        list_level_tokens = []
        nest = 0
        for token in tokens:
            if nest == 1 and token.tag == 'li':
                list_level_tokens.append(token)
            nest += token.nesting

        # Assign them a marking
        margin_width = len(str(len(list_level_tokens)))
        for i, token in enumerate(list_level_tokens, start=1):
            token.attrs['data-margin'] = str(i).rjust(margin_width) + '.'
            token.attrs['data-list-type'] = 'ol'

        # Now render the tokens as normal
        return self.render_block(
            tokens,
            width=width,
            left=left,
        )

    def render_table(
            self,
            tokens: ta.Sequence['Token'],
            width: int,
            left: int = 0,
            border: type[Border] = SquareBorder,
    ) -> ptk.StyleAndTextTuples:
        """
        Render a list of parsed markdown tokens representing a table element.

        Args:
            tokens: The list of parsed tokens to render
            width: The width at which to render the tokens
            left: The position on the current line at which to render the output - used to indent subsequent lines when
                rendering inline blocks like images
            border: The border style to use to render the table
        Returns:
            Formatted text
        """

        ft: ptk.StyleAndTextTuples = []

        # Stack the tokens in the shape of the table
        cell_tokens: list[list[list[Token]]] = []
        i = 0
        while i < len(tokens):
            token = tokens[i]
            if token.type == 'tr_open':
                cell_tokens.append([])
            elif token.type in ('th_open', 'td_open'):
                for j, token in enumerate(tokens[i:]):
                    if token.type in ('th_close', 'td_close'):
                        cell_tokens[-1].append(list(tokens[i:i + j + 1]))
                        break
                i += j
            i += 1

        def _render_token(
                tokens: ta.Sequence['Token'],
                width: int | None = None,
        ) -> ptk.StyleAndTextTuples:
            """Render a token with correct alignment."""

            side = 'left'

            # Check CSS for text alignment
            for style_str in str(tokens[0].attrs.get('style', '')).split(';'):
                if ':' in style_str:
                    key, value = style_str.strip().split(':', 1)
                    if key.strip() == 'text-align':
                        side = value

            # Render with a very long line length if we do not have a width
            ft = self.render(tokens, width=width or 999999)

            # If we do have a width, wrap and apply the alignment
            if width:
                ft = wrap(ft, width)
                ft = align(_SIDES[side], ft, width)

            return ft

        # Find the naive widths of each cell
        cell_renders: list[list[ptk.StyleAndTextTuples]] = []
        cell_widths: list[list[int]] = []
        for row in cell_tokens:
            cell_widths.append([])
            cell_renders.append([])
            for each_tokens in row:
                rendered = _render_token(each_tokens)
                cell_renders[-1].append(rendered)
                cell_widths[-1].append(ptk.fragment_list_width(rendered))

        # Calculate row and column widths, accounting for broders
        col_widths = [
            max([row[i] for row in cell_widths])
            for i in range(len(cell_widths[0]))
        ]

        # Adjust widths and potentially re-render cells. Reduce biggest cells until we fit in width.
        while sum(col_widths) + 3 * (len(col_widths) - 1) + 4 > width:
            idxmax = max(enumerate(col_widths), key=lambda x: x[1])[0]
            col_widths[idxmax] -= 1

        # Re-render changed cells
        for i, row_widths in enumerate(cell_widths):
            for j, new_width in enumerate(col_widths):
                if row_widths[j] != new_width:
                    cell_renders[i][j] = _render_token(
                        cell_tokens[i][j],
                        width=new_width,
                    )

        # Justify cell contents
        for i, renders_row in enumerate(cell_renders):
            for j, cell in enumerate(renders_row):
                cell_renders[i][j] = align(
                    FormattedTextAlign.LEFT,
                    cell,
                    width=col_widths[j],
                )

        # Render table
        style = 'class:md.table.border'

        def _draw_add_border(
                left: str,
                split: str,
                right: str,
        ) -> None:
            ft.append((style, left + border.HORIZONTAL))

            for col_width in col_widths:
                ft.append((style, border.HORIZONTAL * col_width))
                ft.append((style, border.HORIZONTAL + split + border.HORIZONTAL))

            ft.pop()
            ft.append((style, border.HORIZONTAL + right + '\n'))

        # Draw top border
        _draw_add_border(
            border.TOP_LEFT,
            border.TOP_SPLIT,
            border.TOP_RIGHT,
        )

        # Draw each row
        for i, renders_row in enumerate(cell_renders):
            for row_lines in itertools.zip_longest(*map(ptk.split_lines, renders_row)):
                # Draw each line in each row
                ft.append((style, border.VERTICAL + ' '))

                for j, line in enumerate(row_lines):
                    if line is None:
                        line = [('', ' ' * col_widths[j])]
                    ft += line
                    ft.append((style, ' ' + border.VERTICAL + ' '))

                ft.pop()
                ft.append((style, ' ' + border.VERTICAL + '\n'))

            # Draw border between rows
            if i < len(cell_renders) - 1:
                _draw_add_border(
                    border.LEFT_SPLIT,
                    border.CROSS,
                    border.RIGHT_SPLIT,
                )

        # Draw bottom border
        _draw_add_border(
            border.BOTTOM_LEFT,
            border.BOTTOM_SPLIT,
            border.BOTTOM_RIGHT,
        )

        ft.append(('', '\n'))
        return ft

    def __pt_formatted_text__(self) -> ptk.StyleAndTextTuples:
        """Formatted text magic method."""

        return self.formatted_text
