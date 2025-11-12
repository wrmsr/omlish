import ast

from omlish import check


##


class _ParentsNodeVisitor(ast.NodeVisitor):
    def __init__(self) -> None:
        super().__init__()

        self.parents: dict[ast.AST, ast.AST | None] = {}

    parent: ast.AST | None = None

    def generic_visit(self, node: ast.AST) -> None:
        check.not_in(node, self.parents)
        prev_parent = self.parents[node] = self.parent
        self.parent = node
        super().generic_visit(node)
        self.parent = prev_parent


def get_node_parents(node: ast.AST) -> dict[ast.AST, ast.AST | None]:
    visitor = _ParentsNodeVisitor()
    visitor.visit(node)
    return visitor.parents
