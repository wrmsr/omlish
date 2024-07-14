from .._vendor import antlr4
from ..graphs.dot import dot  # noqa
from .antlr import yield_contexts


def dot_ctx(root: antlr4.ParserRuleContext) -> dot.Graph:
    stmts = [
        dot.RawStmt('rankdir=LR;'),
    ]

    for c in yield_contexts(root):
        if isinstance(c, antlr4.TerminalNode):
            continue

        lbl = [
            [type(c).__name__],
            [str(id(c))],
            [f'{c.start} {c.stop}'],
        ]

        stmts.append(dot.Node(f'_{id(c)}', {'label': lbl, 'shape': 'box'}))

        for n in (c.children or []):
            if not isinstance(n, antlr4.TerminalNode):
                stmts.append(dot.Edge(f'_{id(c)}', f'_{id(n)}'))

    return dot.Graph(stmts)


def open_dot_ctx(root: antlr4.ParserRuleContext) -> None:
    dot.open_dot(dot.render(dot_ctx(root)))
