import ast

from omlish import check


##


class StackNodeVisitor(ast.NodeVisitor):
    def __init__(self) -> None:
        super().__init__()

        self.node_stack: list[ast.AST] = []

    def generic_visit(self, node: ast.AST) -> None:
        self.node_stack.append(node)
        super().generic_visit(node)
        check.is_(self.node_stack.pop(), node)
