# ruff: noqa: SLF001
import typing as ta

from omdev.tui import textual as tx
from omlish import dataclasses as dc

from ..inputhistory import InputHistoryManager
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
        self._suppress_suggestions_update: bool = False

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

    def set_mode(self, mode: InputMode) -> bool:
        """Returns if changed."""

        if self._mode == mode:
            return False

        self._mode = mode

        self._ic._input_glyph.content = mode

        self._update_suggestions()

        return True

    def _update_suggestions(self) -> None:
        if self.mode == '/':
            sis = self._ic._suggestions_manager.update_suggestions(self.text)
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
        if self._suppress_suggestions_update:
            self._suppress_suggestions_update = False
            return

        was_cycling = self._ic._suggestions_manager.is_cycling
        if was_cycling:
            self._ic._suggestions_manager.end_cycling()
            self._ic._suggestions_popup.hide()

        text = self.text

        if not text:
            self.set_mode('>')

        elif text[0] == '/':
            if not self.set_mode('/'):
                if not was_cycling:
                    self._update_suggestions()

    async def on_key(self, event: tx.Key) -> None:
        if event.key == 'tab':
            if self._mode == '/':
                selected = self._ic._suggestions_manager.select_next()
                if selected is not None:
                    self._suppress_suggestions_update = True
                    self.text = selected.label + ' '
                    end = self.document.end
                    self.selection = tx.Selection(end, end)

                    self._ic._suggestions_popup.update_suggestions(
                        self._ic._suggestions_manager.get_suggestions() or [],
                    )

                    event.prevent_default()
                    event.stop()


class InputContainer(tx.InitAddClass, tx.ComposeOnce, tx.Static):
    input_add_class = 'input-container'

    def __init__(
            self,
            *,
            input_history_manager: InputHistoryManager,
            suggestions_manager: SuggestionsManager,
            **kwargs: ta.Any,
    ) -> None:
        super().__init__(**kwargs)

        self._input_history_manager = input_history_manager
        self._suggestions_manager = suggestions_manager

        self._input_text_area = InputTextArea(self)
        self._input_glyph = tx.Static('>', classes='input-glyph')
        self._suggestions_popup = SuggestionsPopup(self)

    @property
    def input_text_area(self) -> InputTextArea:
        return self._input_text_area

    #

    def _compose_once(self) -> tx.ComposeResult:
        with tx.Vertical(classes='input-vertical'):
            yield self._suggestions_popup
            with tx.Vertical(classes='input-vertical2'):
                with tx.Horizontal(classes='input-horizontal'):
                    yield self._input_glyph
                    yield self._input_text_area

    #

    def _move_input_cursor_to_end(self) -> None:
        ita = self._input_text_area
        ln = ita.document.line_count - 1
        lt = ita.document.lines[ln]
        ita.move_cursor((ln, len(lt)))

    @tx.on(InputTextArea.HistoryPrevious)
    async def on_input_text_area_history_previous(self, event: InputTextArea.HistoryPrevious) -> None:
        await self._input_history_manager.load_if_necessary()
        if (entry := self._input_history_manager.get_previous(event.text)) is not None:
            self._input_text_area.text = entry
            self._move_input_cursor_to_end()

    @tx.on(InputTextArea.HistoryNext)
    async def on_input_text_area_history_next(self, event: InputTextArea.HistoryNext) -> None:
        await self._input_history_manager.load_if_necessary()
        if (entry := self._input_history_manager.get_next(event.text)) is not None:
            ita = self._input_text_area
            ita.text = entry
            self._move_input_cursor_to_end()
        else:
            # At the end of history, clear the input
            ita = self._input_text_area
            ita.clear()
            self._input_history_manager.reset_position()
