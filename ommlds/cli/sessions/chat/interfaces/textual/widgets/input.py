import dataclasses as dc
import typing as ta

from omdev.tui import textual as tx


##


class InputTextArea(tx.TextArea):
    @dc.dataclass()
    class Submitted(tx.Message):
        text: str

    @dc.dataclass()
    class HistoryPrevious(tx.Message):
        text: str

    @dc.dataclass()
    class HistoryNext(tx.Message):
        text: str

    @dc.dataclass()
    class HistoryReset(tx.Message):
        pass

    def __init__(self, **kwargs: ta.Any) -> None:
        super().__init__(**kwargs)

    BINDINGS: ta.ClassVar[ta.Sequence[tx.Binding]] = [  # type: ignore[assignment]
        tx.Binding(
            'enter',
            'submit',
            priority=True,
        ),
        tx.Binding(
            'ctrl+p',
            'history_previous',
        ),
        tx.Binding(
            'ctrl+n',
            'history_next',
        ),
    ]

    def action_submit(self) -> None:
        if text := self.text.strip():
            self.post_message(self.Submitted(text))

    def action_cursor_up(self, select: bool = False) -> None:
        # FIXME: if empty -> history_previous
        super().action_cursor_up(select=select)

    def action_cursor_down(self, select: bool = False) -> None:
        super().action_cursor_down(select=select)

    def action_history_previous(self) -> None:
        self.post_message(self.HistoryPrevious(self.text))

    def action_history_next(self) -> None:
        self.post_message(self.HistoryNext(self.text))


class InputOuter(tx.Static):
    def compose(self) -> tx.ComposeResult:
        with tx.Vertical(id='input-vertical'):
            with tx.Vertical(id='input-vertical2'):
                with tx.Horizontal(id='input-horizontal'):
                    yield tx.Static('>', id='input-glyph')
                    yield InputTextArea(placeholder='...', id='input')
