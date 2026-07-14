# ruff: noqa: SLF001
import typing as ta

from omdev.tui import textual as tx
from omcore import dataclasses as dc
from omcore import lang


if ta.TYPE_CHECKING:
    from .base import Message


##


@dc.dataclass()
class MessageDividerClicked(tx.Event):
    event: tx.Click


class MessageDivider(
    tx.InitAddClass,
    tx.Static,
):
    init_add_class = 'message-divider'

    def __init__(
            self,
            *,
            left_text: str | None = None,
            center_text: str | None = None,
            right_text: str | None = None,
            line_style: ta.Any | None = None,
            text_style: ta.Any | None = None,
    ) -> None:
        super().__init__()

        self._left_text = left_text
        self._center_text = center_text
        self._right_text = right_text
        self._line_style = line_style
        self._text_style = text_style

        self._refresh()

    @classmethod
    def for_message(cls, msg: Message) -> MessageDivider:
        return cls(
            # left_text=str(cu) if (cu := msg.messages_container.chat_uuid) is not None else None,
            center_text=lang.localnow().strftime('%Y-%m-%d %H:%M:%S'),
            right_text=str(mu) if (mu := msg.message_uuid) is not None else None,
        )

    def on_click(self, event: tx.Click) -> None:
        if event.button != 1:
            return

        event.stop()

        self.post_message(MessageDividerClicked(event))

    def _refresh(self) -> None:
        if (text_style := self._text_style) is None:
            text_style = tx.RichStyle(color=self.rich_style.color)

        def make_text(s):
            return tx.Text(s, style=text_style) if s else ''  # noqa

        if (line_style := self._line_style) is None:
            line_style = tx.RichStyle(color=self.app.current_theme.primary)

        self.update(
            tx.RichTriRule(
                left=make_text(self._left_text),
                center=make_text(self._center_text),
                right=make_text(self._right_text),
                style=line_style,
                left_pad=1,
                right_pad=1,
            ),
        )
