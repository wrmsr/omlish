from omdev.tui import rich

from ...facades.text import CanFacadeText
from ...facades.text import ConcatFacadeText
from ...facades.text import FacadeText
from ...facades.text import FacadeTextStyle
from ...facades.text import StrFacadeText
from ...facades.text import StyleFacadeText
from ...facades.ui import UiMessageDisplayer
from .app import ChatAppGetter


##


def facade_text_to_rich_text(t: CanFacadeText) -> rich.Text:
    """Convert FacadeText tree into rich.Text with correct nested style inheritance."""

    root = FacadeText.of(t)
    out = rich.Text()

    def merge_style(
            parent: FacadeTextStyle,
            child: FacadeTextStyle,
    ) -> FacadeTextStyle:
        return FacadeTextStyle(
            color=child.color if child.color is not None else parent.color,
            bold=child.bold if child.bold is not None else parent.bold,
            italic=child.italic if child.italic is not None else parent.italic,
        )

    def to_rich_style(s: FacadeTextStyle) -> rich.Style | None:
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

    def visit(node: FacadeText, style: FacadeTextStyle) -> None:
        if isinstance(node, StrFacadeText):
            if node.s:
                out.append(node.s, style=to_rich_style(style))

        elif isinstance(node, ConcatFacadeText):
            for c in node.l:
                visit(c, style)

        elif isinstance(node, StyleFacadeText):
            new_style = merge_style(style, node.y)
            visit(node.c, new_style)

        else:
            raise TypeError(node)

    visit(root, FacadeTextStyle.DEFAULT)

    return out


##


class ChatAppUiMessageDisplayer(UiMessageDisplayer):
    def __init__(
            self,
            *,
            app: ChatAppGetter,
    ) -> None:
        super().__init__()

        self._app = app

    async def display_ui_message(self, text: CanFacadeText) -> None:
        rt = facade_text_to_rich_text(text)
        await (await self._app()).display_ui_message(rt)
