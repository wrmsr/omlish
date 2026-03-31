from omdev.tui import rich

from ...... import minichain as mc
from .types import ChatAppGetter


##


def facade_text_to_rich_text(t: mc.facades.CanFacadeText) -> rich.Text:
    """Convert FacadeText tree into rich.Text with correct nested style inheritance."""

    root = mc.facades.FacadeText.of(t)
    out = rich.Text()

    def merge_style(
            parent: mc.facades.FacadeTextStyle,
            child: mc.facades.FacadeTextStyle,
    ) -> mc.facades.FacadeTextStyle:
        return mc.facades.FacadeTextStyle(
            color=child.color if child.color is not None else parent.color,
            bold=child.bold if child.bold is not None else parent.bold,
            italic=child.italic if child.italic is not None else parent.italic,
        )

    def to_rich_style(s: mc.facades.FacadeTextStyle) -> rich.Style | None:
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

    def visit(node: mc.facades.FacadeText, style: mc.facades.FacadeTextStyle) -> None:
        if isinstance(node, mc.facades.StrFacadeText):
            if node.s:
                out.append(node.s, style=to_rich_style(style))

        elif isinstance(node, mc.facades.ConcatFacadeText):
            for c in node.l:
                visit(c, style)

        elif isinstance(node, mc.facades.StyleFacadeText):
            new_style = merge_style(style, node.y)
            visit(node.c, new_style)

        else:
            raise TypeError(node)

    visit(root, mc.facades.FacadeTextStyle.DEFAULT)

    return out


##


class ChatAppUiMessageDisplayer(mc.facades.UiMessageDisplayer):
    def __init__(
            self,
            *,
            app: ChatAppGetter,
    ) -> None:
        super().__init__()

        self._app = app

    async def display_ui_message(self, text: mc.facades.CanFacadeText) -> None:
        rt = facade_text_to_rich_text(text)
        await (await self._app()).display_ui_message(rt)
