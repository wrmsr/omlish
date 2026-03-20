from ... import rich
from ... import textual as tx


##


HIGHLIGHTER = rich.ReprHighlighter()


class JsonDocument(tx.Static):
    def load(self, json_data: str) -> bool:
        try:
            # TODO: Customize theme="github-dark"
            json_doc = rich.Syntax(json_data, lexer='json', line_numbers=True)
        except Exception as e:  # noqa
            return False
        self.update(json_doc)
        return True


class JsonDocumentView(tx.Vertical):
    DEFAULT_CSS = """
        JsonDocumentView {
            height: 1fr;
            overflow: auto;
        }

        JsonDocumentView > Static {
            width: auto;
        }
    """

    def compose(self) -> tx.ComposeResult:
        yield JsonDocument(id='json-document')


class JsonTree(tx.Tree):
    def add_node(self, name: str, node: tx.TreeNode, data: object) -> None:
        """
        Adds a node to the tree.

        Args:
            name (str): Name of the node.
            node (TreeNode): Parent node.
            data (object): Data associated with the node.
        """

        if isinstance(data, dict):
            node._label = rich.Text(f'{{}} {name}')  # noqa
            for key, value in data.items():
                new_node = node.add('')
                self.add_node(key, new_node, value)
        elif isinstance(data, list):
            node._label = rich.Text(f'[] {name}')  # noqa
            for index, value in enumerate(data):
                new_node = node.add('')
                self.add_node(str(index), new_node, value)
        else:
            node._allow_expand = False  # noqa
            if name:
                label = rich.Text.assemble(
                    rich.Text.from_markup(f'[b]{name}[/b]='), HIGHLIGHTER(repr(data)),
                )
            else:
                label = rich.Text(repr(data))
            node._label = label  # noqa


class TreeView(tx.Widget, can_focus_children=True):
    def compose(self) -> tx.ComposeResult:
        tree = JsonTree('Root')
        tree.show_root = False
        yield tree
