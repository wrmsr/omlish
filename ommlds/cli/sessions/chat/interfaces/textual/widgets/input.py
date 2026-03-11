# ruff: noqa: SLF001
import typing as ta

from omdev.tui import textual as tx
from omlish import dataclasses as dc

from ..suggestions import SuggestionItem
from ..suggestions import SuggestionsManager


##


class SuggestionsPopup(tx.InitAddClass, tx.Static):
    init_add_class = 'suggestions-popup'

    def __init__(self, ic: 'InputContainer', **kwargs: ta.Any) -> None:
        super().__init__(**kwargs)

        self._ic = ic

        self.styles.display = 'none'
        self.can_focus = False

    def hide(self) -> None:
        self.update('')
        self.styles.display = 'none'

    def show(self) -> None:
        self.styles.display = 'block'

    def update_suggestions(self, items: ta.Sequence[SuggestionItem]) -> None:
        if not items:
            self.hide()
            return

        txt = tx.Text()

        mll = max(len(ci.label or ' ') for ci in items)

        for i, ci in enumerate(items):
            if i:
                txt.append('\n')

            l = ci.label or ' '
            txt.append(l, style='bold reverse' if ci.selected else 'bold')
            if ci.description:
                txt.append(' ' * (mll - len(l or ' ') + 2))
                txt.append(ci.description, style='italic' if ci.selected else 'dim')

        self.update(txt)
        self.show()


InputMode: ta.TypeAlias = ta.Literal['>', '/']


class InputTextArea(tx.InitAddClass, tx.TextArea):
    init_add_class = 'input'

    def __init__(self, ic: 'InputContainer', **kwargs: ta.Any) -> None:
        super().__init__(
            placeholder='...',
            **kwargs,
        )

        self._ic = ic

        self._mode: InputMode = '>'

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

    @property
    def mode(self) -> InputMode:
        return self._mode

    def set_mode(self, mode: InputMode) -> None:
        if self._mode == mode:
            return

        self._mode = mode

        self._ic._input_glyph.content = mode

        if mode == '/':
            sis = self._ic._suggestions_manager.get_suggestions()
            self._ic._suggestions_popup.update_suggestions(sis)
        else:
            self._ic._suggestions_popup.hide()

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

    async def on_text_area_changed(self, event: tx.TextArea.Changed) -> None:
        text = self.text

        if not text:
            self.set_mode('>')
        elif text[0] == '/':
            self.set_mode('/')


class InputContainer(tx.InitAddClass, tx.ComposeOnce, tx.Static):
    input_add_class = 'input-container'

    def __init__(
            self,
            *,
            suggestions_manager: SuggestionsManager,
            **kwargs: ta.Any,
    ) -> None:
        super().__init__(**kwargs)

        self._suggestions_manager = suggestions_manager

        self._input_text_area = InputTextArea(self)
        self._input_glyph = tx.Static('>', classes='input-glyph')
        self._suggestions_popup = SuggestionsPopup(self)

    def _compose_once(self) -> tx.ComposeResult:
        with tx.Vertical(classes='input-vertical'):
            yield self._suggestions_popup
            with tx.Vertical(classes='input-vertical2'):
                with tx.Horizontal(classes='input-horizontal'):
                    yield self._input_glyph
                    yield self._input_text_area
