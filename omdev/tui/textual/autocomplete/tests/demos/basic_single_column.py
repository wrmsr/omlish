"""Basic dropdown autocomplete from a list of options."""
from textual.app import App
from textual.app import ComposeResult
from textual.containers import Container
from textual.widgets import Input

from ...widget import AutoComplete


##


LANGUAGES = [
    'Python',
    'JavaScript',
    'TypeScript',
    'Java',
    'C++',
    'Ruby',
    'Go',
    'Rust',
]


class AutoCompleteExample(App[None]):
    def compose(self) -> ComposeResult:
        with Container(id='container'):
            text_input = Input(placeholder='Search for a programming language...')
            yield text_input

            yield AutoComplete(
                target=text_input,  # The widget to attach autocomplete to
                candidates=LANGUAGES,  # The list of completion candidates
            )


if __name__ == '__main__':
    app = AutoCompleteExample()
    app.run()
