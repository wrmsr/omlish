import codeop
import re
import typing as ta

from omdev.tui import textual as tx

from .completion import common_prefix
from .completion import extract_stem


if ta.TYPE_CHECKING:
    from .completion import CompletionPopup
    from .completion import CompletionProvider


##


def _strip_final_indent(text: str) -> str:
    """Strip trailing auto-indent whitespace (spaces/tabs after final newline)."""

    short = text.rstrip(' \t')
    n = len(short)
    if n > 0 and text[n - 1] == '\n':
        return short
    return text


_DEDENT_KEYWORDS = frozenset({'return', 'break', 'continue', 'pass', 'raise'})


class CodeInput(tx.TextArea):
    """Python code input with smart Enter, auto-indent, history, and completion."""

    class Submitted(tx.Message):
        def __init__(self, code: str) -> None:
            super().__init__()
            self.code = code

    BINDINGS = [  # noqa
        tx.Binding('enter', 'submit_or_newline', 'Run', show=False, priority=True),
        tx.Binding('up', 'history_or_up', show=False, priority=True),
        tx.Binding('down', 'history_or_down', show=False, priority=True),
        tx.Binding('tab', 'complete', show=False, priority=True),
        tx.Binding('escape', 'dismiss_completion', show=False),
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(
            language='python',
            tab_behavior='indent',
            **kwargs,
        )

        # History
        self._history: list[str] = []
        self._history_index: int = 0
        self._current_edit: str = ''

        # Completion
        self._completion_provider: CompletionProvider | None = None
        self._completion_popup: CompletionPopup | None = None
        self._completions: list[str] = []
        self._completion_stem: str = ''
        self._last_action_was_complete: bool = False

    def set_completion(
        self,
        provider: 'CompletionProvider',
        popup: 'CompletionPopup',
    ) -> None:
        self._completion_provider = provider
        self._completion_popup = popup

    @property
    def _popup_visible(self) -> bool:
        return self._completion_popup is not None and self._completion_popup.display

    # Key event: dismiss popup on unrelated keys

    def on_key(self, event) -> None:
        if event.key not in ('tab', 'up', 'down', 'enter', 'escape'):
            self._dismiss_completion()
            self._last_action_was_complete = False

    # Completeness detection

    def _is_complete(self, source: str) -> bool | None:
        """True=complete, False=error(submit), None=incomplete(need more)."""

        stripped = _strip_final_indent(source)
        try:
            result = codeop.compile_command(stripped, '<input>', 'exec')
        except (SyntaxError, OverflowError, ValueError):
            lines = stripped.splitlines(keepends=True)
            if len(lines) <= 1:
                return False
            last_line = lines[-1]
            was_indented = last_line.startswith((' ', '\t'))
            not_empty = last_line.strip() != ''
            incomplete = not last_line.endswith('\n')
            if (was_indented or not_empty) and incomplete:
                return None
            return False
        else:
            return None if result is None else True

    # Auto-indent

    def _get_auto_indent(self, text: str) -> str:
        lines = text.split('\n')
        last_line = ''
        for line in reversed(lines):
            if line.strip():
                last_line = line
                break
        if not last_line:
            return ''

        indent = len(last_line) - len(last_line.lstrip())
        indent_str = last_line[:indent]

        stripped = re.sub(r'#.*$', '', last_line).rstrip()
        if stripped.endswith(':'):
            indent_str += '    '
        else:
            first_word = last_line.strip().split()[0] if last_line.strip() else ''
            if first_word in _DEDENT_KEYWORDS and len(indent_str) >= 4:
                indent_str = indent_str[:-4]

        return indent_str

    # Submit / newline

    def action_submit_or_newline(self) -> None:
        if self._popup_visible:
            if self._completion_popup is not None:
                selected = self._completion_popup.get_selected()
                if selected:
                    self._insert_completion(selected, self._completion_stem)
            return

        text = self.text
        if not text.strip():
            return

        completeness = self._is_complete(text)

        if completeness is None:
            indent = self._get_auto_indent(text)
            self.insert('\n' + indent)
            return

        submitted = _strip_final_indent(text)
        if submitted.strip():
            if not self._history or self._history[-1] != submitted:
                self._history.append(submitted)
            self._history_index = len(self._history)
            self._current_edit = ''
        self.post_message(self.Submitted(submitted))
        self.text = ''

    # History

    def action_history_or_up(self) -> None:
        if self._popup_visible:
            popup = self._completion_popup
            if popup is not None and popup.highlighted is not None and popup.highlighted > 0:
                popup.highlighted -= 1
            return

        row, _ = self.cursor_location
        if row == 0 and self._history and self._history_index > 0:
            if self._history_index == len(self._history):
                self._current_edit = self.text
            self._history_index -= 1
            self.text = self._history[self._history_index]
            self._move_cursor_to_end()
        else:
            self.action_cursor_up()

    def action_history_or_down(self) -> None:
        if self._popup_visible:
            popup = self._completion_popup
            if popup is not None and popup.highlighted is not None and popup.highlighted < popup.option_count - 1:
                popup.highlighted += 1
            return

        row, _ = self.cursor_location
        if row == self.document.line_count - 1 and self._history_index < len(self._history):
            self._history_index += 1
            if self._history_index == len(self._history):
                self.text = self._current_edit
            else:
                self.text = self._history[self._history_index]
            self._move_cursor_to_end()
        else:
            self.action_cursor_down()

    def _move_cursor_to_end(self) -> None:
        last = self.document.line_count - 1
        self.cursor_location = (last, len(self.document.get_line(last)))

    # Completion

    def action_complete(self) -> None:
        if self._popup_visible:
            if self._completion_popup is not None:
                selected = self._completion_popup.get_selected()
                if selected:
                    self._insert_completion(selected, self._completion_stem)
                else:
                    self._dismiss_completion()
            return

        if self._completion_provider is None:
            self.insert('    ')
            return

        row, col = self.cursor_location
        line = self.document.get_line(row)
        stem = extract_stem(line, col)

        if not stem:
            self.insert('    ')
            return

        if not self._last_action_was_complete:
            completions = self._completion_provider.get_completions(stem)
            if not completions:
                return
            if len(completions) == 1:
                self._insert_completion(completions[0], stem)
                return
            self._completions = completions
            self._completion_stem = stem
            pfx = common_prefix(completions, len(stem))
            if pfx:
                self.insert(pfx)
            self._last_action_was_complete = True
        else:
            if self._completion_popup and self._completions:
                self._completion_popup.show(self._completions, self._completion_stem)

    def _insert_completion(self, completion: str, stem: str) -> None:
        suffix = completion[len(stem):]
        self.insert(suffix)
        self._dismiss_completion()

    def action_dismiss_completion(self) -> None:
        self._dismiss_completion()

    def _dismiss_completion(self) -> None:
        self._completions = []
        self._completion_stem = ''
        self._last_action_was_complete = False
        if self._completion_popup:
            self._completion_popup.dismiss()
