from omdev.tui import rich

from .text import CanUiText
from .text import ConcatUiText
from .text import DiffUiText
from .text import StrUiText
from .text import StyleUiText
from .text import UiText
from .text import UiTextStyle


##


def ui_text_to_rich_text(t: CanUiText) -> rich.Text:
    """Convert UiText tree into rich.Text with correct nested style inheritance."""

    root = UiText.of(t)
    out = rich.Text()

    def merge_style(
            parent: UiTextStyle,
            child: UiTextStyle,
    ) -> UiTextStyle:
        return UiTextStyle(
            color=child.color if child.color is not None else parent.color,
            bold=child.bold if child.bold is not None else parent.bold,
            italic=child.italic if child.italic is not None else parent.italic,
        )

    def to_rich_style(s: UiTextStyle) -> rich.Style | None:
        if (
                s.color is None and
                s.bold is None and
                s.italic is None
        ):
            return None

        return rich.Style(
            color=s.color,
            bold=s.bold,
            italic=s.italic,
        )

    def visit(node: UiText, style: UiTextStyle) -> None:
        if isinstance(node, StrUiText):
            if node.s:
                out.append(node.s, style=to_rich_style(style))

        elif isinstance(node, ConcatUiText):
            for c in node.l:
                visit(c, style)

        elif isinstance(node, StyleUiText):
            new_style = merge_style(style, node.y)
            visit(node.c, new_style)

        elif isinstance(node, DiffUiText):
            for l in node.diff_lines:
                if not l.endswith('\n'):
                    l += '\n'

                if l.startswith('+'):
                    out.append(l, style=rich.Style(color='green'))
                elif l.startswith('-'):
                    out.append(l, style=rich.Style(color='red'))
                elif l.startswith('@@'):
                    out.append(l, style=rich.Style(color='cyan'))
                else:
                    out.append(l, style=to_rich_style(style))

        else:
            raise TypeError(node)

    visit(root, UiTextStyle.DEFAULT)

    return out
