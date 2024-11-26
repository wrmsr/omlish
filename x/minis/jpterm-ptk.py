import argparse
import json
import sys

from prompt_toolkit import Application
from prompt_toolkit.input.defaults import create_input
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import HSplit
from prompt_toolkit.layout import Layout
from prompt_toolkit.layout import VSplit
from prompt_toolkit.layout import Window
from prompt_toolkit.layout.dimension import D
from prompt_toolkit.lexers import PygmentsLexer
from prompt_toolkit.widgets import Label
from prompt_toolkit.widgets import TextArea
from pygments.lexers import JsonLexer

from omlish.specs import jmespath


class JmespathDisplay:
    def __init__(self, input_data):
        super().__init__()

        self.parsed_json = input_data
        self.last_result = None
        self.last_expression = None

        self.expression_input = TextArea(
            height=1,
            prompt="Jmespath Expression: ",
            multiline=False,
            wrap_lines=False
        )

        self.input_json_area = TextArea(
            text=json.dumps(self.parsed_json, indent=2),
            read_only=True,
            lexer=PygmentsLexer(JsonLexer),
            scrollbar=True
        )

        self.result_area = TextArea(
            text="",
            read_only=True,
            lexer=PygmentsLexer(JsonLexer),
            scrollbar=True
        )

        self.status_bar = Label("Status: ")

        self._setup_key_bindings()

    def _evaluate_expression(self, expression):
        if not expression:
            self.result_area.text = ""
            return

        try:
            options = jmespath.Options()
            result = jmespath.compile(expression).search(self.parsed_json, options)
            if result is not None:
                self.last_result = result
                self.result_area.text = json.dumps(result, indent=2)
                self.status_bar.text = "Status: success"
                
            else:
                self.result_area.text = ""
                
        except Exception as e:
            self.status_bar.text = f"Status: error - {e}"

    def _setup_key_bindings(self):
        kb = KeyBindings()

        @kb.add("c-c")
        @kb.add("f5")
        def exit_(event):
            event.app.exit()

        @kb.add("enter")
        def evaluate(event):
            self.last_expression = self.expression_input.text
            self._evaluate_expression(self.last_expression)

        self.key_bindings = kb

    def create_layout(self):
        main_content = VSplit(
            [
                self.input_json_area,
                Window(width=1, style="class:line"),
                self.result_area,
            ],
            height=D(),
        )

        return Layout(
            HSplit([
                self.expression_input,
                main_content,
                self.status_bar,
            ]),
        )

    def run(self):
        layout = self.create_layout()
        input = create_input(sys.stdout)
        app = Application(
            input=input,
            layout=layout,
            key_bindings=self.key_bindings,
            full_screen=True,
        )
        app.run()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('input')
    args = parser.parse_args()

    if args.input == '-':
        input_json = json.loads(sys.stdin.read())
    else:
        with open(args.input) as f:
            input_json = json.load(f)

    # input_json = {  # FIXME
    #     'a': 'foo',
    #     'b': 'bar',
    # }

    display = JmespathDisplay(input_json)
    display.run()


if __name__ == '__main__':
    sys.exit(main())
