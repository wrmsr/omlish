import typing as ta

from ..graphs import dot
from . import runtime as antlr4
from .utils import yield_contexts


def dot_ctx(
        root: antlr4.ParserRuleContext,
        *,
        left_to_right: bool = False,
) -> dot.Graph:
    stmts: list[dot.Stmt] = []

    if left_to_right:
        stmts.append(dot.RawStmt('rankdir=LR;'))

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


def open_dot_ctx(root: antlr4.ParserRuleContext, **kwargs: ta.Any) -> None:
    dot.open_dot(dot.render(dot_ctx(root)), **kwargs)
