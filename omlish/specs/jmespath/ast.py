import typing as ta


class Node(ta.TypedDict):
    type: str
    children: list['Node']
    value: ta.NotRequired[ta.Any]


def arithmetic_unary(operator: str, expression: Node) -> Node:
    return {
        'type': 'arithmetic_unary',
        'children': [expression],
        'value': operator,
    }


def arithmetic(operator: str, left: Node, right: Node) -> Node:
    return {
        'type': 'arithmetic',
        'children': [left, right],
        'value': operator,
    }


def assign(name: str, expr: Node) -> Node:
    return {
        'type': 'assign',
        'children': [expr],
        'value': name,
    }


def comparator(name: str, first: Node, second: Node) -> Node:
    return {
        'type': 'comparator',
        'children': [first, second],
        'value': name,
    }


def current_node() -> Node:
    return {
        'type': 'current',
        'children': [],
    }


def root_node() -> Node:
    return {
        'type': 'root',
        'children': [],
    }


def expref(expression: Node) -> Node:
    return {
        'type': 'expref',
        'children': [expression],
    }


def function_expression(name: str, args: list[Node]) -> Node:
    return {
        'type': 'function_expression',
        'children': args,
        'value': name,
    }


def field(name: str) -> Node:
    return {
        'type': 'field',
        'children': [],
        'value': name,
    }


def filter_projection(left: Node, right: Node, comparator: Node) -> Node:  # noqa
    return {
        'type': 'filter_projection',
        'children': [left, right, comparator],
    }


def flatten(node: Node) -> Node:
    return {
        'type': 'flatten',
        'children': [node],
    }


def identity() -> Node:
    return {
        'type': 'identity',
        'children': [],
    }


def index(index: int) -> Node:
    return {
        'type': 'index',
        'children': [],
        'value': index,
    }


def index_expression(children: list[Node]) -> Node:
    return {
        'type': 'index_expression',
        'children': children,
    }


def key_val_pair(key_name: str, node: Node) -> Node:
    return {
        'type': 'key_val_pair',
        'children': [node],
        'value': key_name,
    }


def let_expression(bindings: list[Node], expr: Node) -> Node:
    return {
        'type': 'let_expression',
        'children': [*bindings, expr],
    }


def literal(literal_value: ta.Any) -> Node:
    return {
        'type': 'literal',
        'children': [],
        'value': literal_value,
    }


def multi_select_dict(nodes: list[Node]) -> Node:
    return {
        'type': 'multi_select_dict',
        'children': nodes,
    }


def multi_select_list(nodes: list[Node]) -> Node:
    return {
        'type': 'multi_select_list',
        'children': nodes,
    }


def or_expression(left: Node, right: Node) -> Node:
    return {
        'type': 'or_expression',
        'children': [left, right],
    }


def and_expression(left: Node, right: Node) -> Node:
    return {
        'type': 'and_expression',
        'children': [left, right],
    }


def not_expression(expr: Node) -> Node:
    return {
        'type': 'not_expression',
        'children': [expr],
    }


def pipe(left: Node, right: Node) -> Node:
    return {
        'type': 'pipe',
        'children': [left, right],
    }


def projection(left: Node, right: Node) -> Node:
    return {
        'type': 'projection',
        'children': [left, right],
    }


def subexpression(children: list[Node]) -> Node:
    return {
        'type': 'subexpression',
        'children': children,
    }


def slice(start, end, step) -> Node:  # noqa
    return {
        'type': 'slice',
        'children': [],
        'value': (start, end, step),
    }


def value_projection(left: Node, right: Node) -> Node:
    return {
        'type': 'value_projection',
        'children': [left, right],
    }


def variable_ref(name: str) -> Node:
    return {
        'type': 'variable_ref',
        'children': [],
        'value': name,
    }
