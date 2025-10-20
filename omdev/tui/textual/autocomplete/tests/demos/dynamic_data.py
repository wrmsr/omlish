from textual.app import App
from textual.app import ComposeResult
from textual.widgets import Input

from ... import AutoComplete
from ... import AutoCompleteItem


##


class DynamicDataApp(App[None]):
    CSS = """
    Input {
        margin: 2 4;
    }
    """

    def compose(self) -> ComposeResult:
        input_widget = Input()
        yield input_widget
        yield AutoComplete(input_widget, candidates=self.get_candidates)

    def get_candidates(self, state: AutoComplete.TargetState) -> list[AutoCompleteItem]:
        left = len(state.text)
        return [
            AutoCompleteItem(item, prefix=f'{left:>2} ')
            for item in [
                'Apple',
                'Banana',
                'Cherry',
                'Orange',
                'Pineapple',
                'Strawberry',
                'Watermelon',
            ]
        ]


if __name__ == '__main__':
    app = DynamicDataApp()
    app.run()
