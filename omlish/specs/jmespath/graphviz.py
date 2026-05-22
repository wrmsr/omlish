import typing as ta

from ... import lang
from .ast import Arithmetic
from .ast import ArithmeticUnary
from .ast import Assign
from .ast import Comparator
from .ast import Field
from .ast import FunctionExpression
from .ast import Index
from .ast import KeyValPair
from .ast import Literal
from .ast import Node
from .ast import VariableRef
from .visitor import node_type


if ta.TYPE_CHECKING:
    import html
    import json
else:
    html = lang.proxy_import('html')
    json = lang.proxy_import('json')


##


class GraphvizVisitor:
    def __init__(self) -> None:
        super().__init__()

        self._lines: list[str] = []
        self._count = 1

    def visit(self, node: Node) -> str:
        self._lines.append('digraph AST {')
        current = f'{node_type(node)}{self._count}'
        self._count += 1
        self._visit(node, current)
        self._lines.append('}')
        return '\n'.join(self._lines)

    def _node_value(self, node: Node) -> lang.Maybe[ta.Any]:
        if isinstance(node, (ArithmeticUnary, Arithmetic)):
            return lang.just(node.operator)
        elif isinstance(node, (Assign, Comparator, FunctionExpression, Field, VariableRef)):
            return lang.just(node.name)
        elif isinstance(node, Index):
            return lang.just(node.index)
        elif isinstance(node, KeyValPair):
            return lang.just(node.key_name)
        elif isinstance(node, Literal):
            return lang.just(node.literal_value)
        else:
            return lang.empty()

    def _visit(self, node: Node, current: str) -> None:
        self._lines.append(
            f'{current} '
            f'[label="{node_type(node)}({self._node_value(node).map(json.dumps).map(html.escape).or_else("")})"]',
        )
        for child in node.children:
            child_name = f'{node_type(child)}{self._count}'
            self._count += 1
            self._lines.append(f'  {current} -> {child_name}')
            self._visit(child, child_name)
