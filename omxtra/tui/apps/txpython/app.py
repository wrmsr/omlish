import sys
import typing as ta

from omdev.tui import rich
from omdev.tui import textual as tx

from .codeinput import CodeInput
from .completion import CompletionPopup
from .completion import CompletionProvider
from .interpreter import Interpreter


##


class PythonReplApp(tx.App):
    """A Textual-based Python REPL."""

    TITLE = 'txpython'

    CSS = """
        #output {
            height: 1fr;
            background: $surface;
            border: solid $primary;
            padding: 0 1;
        }
        #completion-popup {
            display: none;
            height: auto;
            max-height: 8;
            border: solid $accent;
            background: $boost;
        }
        #input {
            height: auto;
            max-height: 12;
            min-height: 3;
            border: solid $accent;
        }
    """

    BINDINGS: ta.ClassVar[ta.Sequence[tx.BindingType]] = [
        tx.Binding('ctrl+d', 'quit', 'Quit'),
        tx.Binding('ctrl+l', 'clear_output', 'Clear'),
    ]

    def __init__(self) -> None:
        super().__init__()

        self.interpreter = Interpreter()

    def compose(self) -> tx.ComposeResult:
        yield tx.Header()
        yield tx.RichLog(id='output', highlight=True, markup=False, wrap=True)
        yield CompletionPopup(id='completion-popup')
        yield CodeInput(id='input')
        yield tx.Footer()

    def on_mount(self) -> None:
        output = self.query_one('#output', tx.RichLog)
        output.write(rich.Text(f'Python {sys.version}', style='dim'))
        output.write(rich.Text('Enter=run | Tab=complete | Ctrl+D=quit | Ctrl+L=clear', style='dim italic'))
        output.write('')

        code_input = self.query_one('#input', CodeInput)
        code_input.set_completion(
            CompletionProvider(self.interpreter.namespace),
            self.query_one('#completion-popup', CompletionPopup),
        )
        code_input.focus()

    def on_code_input_submitted(self, event: CodeInput.Submitted) -> None:
        output = self.query_one('#output', tx.RichLog)
        source = event.code

        lines = source.split('\n')
        prompt_lines = []
        for i, line in enumerate(lines):
            prefix = '>>> ' if i == 0 else '... '
            prompt_lines.append(prefix + line)
        prompt_text = '\n'.join(prompt_lines)
        output.write(rich.Syntax(prompt_text, 'python', theme='monokai'))

        stdout, stderr = self.interpreter.execute(source)

        if stdout:
            output.write(rich.Text(stdout.rstrip('\n')))
        if stderr:
            output.write(rich.Text(stderr.rstrip('\n'), style='red'))

        output.scroll_end()

    def action_clear_output(self) -> None:
        self.query_one('#output', tx.RichLog).clear()


def _main() -> None:
    app = PythonReplApp()
    app.run()


if __name__ == '__main__':
    _main()
