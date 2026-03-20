import io
import json
import sys
import typing as ta

from omlish import lang

from ... import textual as tx
from .utils import clean_string_values
from .widgets import JsonDocument
from .widgets import JsonDocumentView
from .widgets import JsonTree
from .widgets import TreeView


##


@lang.cached_function
def read_app_css() -> str:
    return lang.get_relative_resources('styles', globals=globals())['layout.tcss'].read_text()


class JsonTreeApp(tx.App):
    CSS: ta.ClassVar[str] = read_app_css()

    BINDINGS = [  # noqa
        ('ctrl+s', 'app.screenshot()', 'Screenshot'),
        ('ctrl+t', 'toggle_root', 'Toggle root'),
        tx.Binding('ctrl+q', 'app.quit', 'Quit'),
    ]

    def __init__(self, json_file: io.TextIOWrapper) -> None:
        super().__init__()

        self.json_data: str = ''

        if json_file is sys.stdin:
            self.json_data = ''.join(sys.stdin.readlines())
        else:
            self.json_data = json_file.read()
            json_file.close()

    def compose(self) -> tx.ComposeResult:
        yield tx.Header()
        yield tx.Container(
            TreeView(id='tree-view'),
            JsonDocumentView(id='json-docview'),
            id='app-grid',
        )
        yield tx.Footer()

    def on_mount(self) -> None:
        tree = self.query_one(JsonTree)
        root_name = 'Json'
        json_node = tree.root.add(root_name)
        json_data = clean_string_values(json.loads(self.json_data))
        tree.add_node(root_name, json_node, json_data)
        json_doc = self.query_one(JsonDocument)
        json_doc.load(json.dumps(json_data, indent=4))

    def action_toggle_root(self) -> None:
        tree = self.query_one(JsonTree)
        tree.show_root = not tree.show_root
