import ast


def dfs_walk(node: ast.AST) -> ta.Iterator[ast.AST]:
    """Helper to iterate over an AST depth-first."""

    stack = [node]
    while stack:
        node = stack.pop()
        stack.extend(reversed(list(ast.iter_child_nodes(node))))
        yield node
