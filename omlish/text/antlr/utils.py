# ruff: noqa: N802 N803
import io
import typing as ta

from . import runtime as antlr4


##


def pformat(
        node: ta.Any,
        *,
        buf: ta.IO | None = None,
        indent: str = '',
        child_indent: str = '  ',
) -> ta.IO:
    if buf is None:
        buf = io.StringIO()
    buf.write(indent)
    buf.write(node.__class__.__name__)
    if hasattr(node, 'start') and hasattr(node, 'stop'):
        buf.write(f' ({node.start} -> {node.stop})')
    buf.write('\n')
    for child in getattr(node, 'children', []) or []:
        pformat(child, buf=buf, indent=indent + child_indent, child_indent=child_indent)
    return buf


def yield_contexts(
        root: antlr4.ParserRuleContext,
) -> ta.Iterator[antlr4.ParserRuleContext]:
    q = [root]
    while q:
        c = q.pop()
        yield c
        if not isinstance(c, antlr4.TerminalNode) and c.children:
            q.extend(c.children)
