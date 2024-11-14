import numbers
import operator
import typing as ta

from ... import check
from .ast import AndExpression
from .ast import Arithmetic
from .ast import ArithmeticUnary
from .ast import Assign
from .ast import Comparator
from .ast import CurrentNode
from .ast import Expref
from .ast import Field
from .ast import FilterProjection
from .ast import Flatten
from .ast import FunctionExpression
from .ast import Identity
from .ast import Index
from .ast import IndexExpression
from .ast import KeyValPair
from .ast import LetExpression
from .ast import Literal
from .ast import MultiSelectDict
from .ast import MultiSelectList
from .ast import Node
from .ast import NotExpression
from .ast import OrExpression
from .ast import Pipe
from .ast import Projection
from .ast import RootNode
from .ast import Slice
from .ast import Subexpression
from .ast import ValueProjection
from .ast import VariableRef
from .exceptions import UndefinedVariableError
from .functions import DefaultFunctions
from .functions import Functions
from .scope import ScopedChainDict


##


def _equals(x: ta.Any, y: ta.Any) -> bool:
    if _is_special_number_case(x, y):
        return False
    else:
        return x == y


def _is_special_number_case(x: ta.Any, y: ta.Any) -> bool | None:
    # We need to special case comparing 0 or 1 to True/False.  While normally comparing any integer other than 0/1 to
    # True/False will always return False.  However 0/1 have this:
    # >>> 0 == True
    # False
    # >>> 0 == False
    # True
    # >>> 1 == True
    # True
    # >>> 1 == False
    # False
    #
    # Also need to consider that:
    # >>> 0 in [True, False]
    # True
    if _is_actual_number(x) and x in (0, 1):
        return isinstance(y, bool)

    elif _is_actual_number(y) and y in (0, 1):
        return isinstance(x, bool)

    else:
        return None


def _is_comparable(x: ta.Any) -> bool:
    # The spec doesn't officially support string types yet, but enough people are relying on this behavior that it's
    # been added back.  This should eventually become part of the official spec.
    return _is_actual_number(x) or isinstance(x, str)


def _is_actual_number(x: ta.Any) -> bool:
    # We need to handle python's quirkiness with booleans, specifically:
    #
    # >>> isinstance(False, int)
    # True
    # >>> isinstance(True, int)
    # True
    if isinstance(x, bool):
        return False
    return isinstance(x, numbers.Number)


##


class Visitor:
    def __init__(self) -> None:
        super().__init__()

        self._method_cache: dict[str, ta.Callable] = {}

    def visit(self, node: Node, *args: ta.Any, **kwargs: ta.Any) -> ta.Any:
        node_type = node['type']
        method = self._method_cache.get(node_type)
        if method is None:
            method = check.not_none(getattr(self, f'visit_{node["type"]}', self.default_visit))
            self._method_cache[node_type] = method
        return method(node, *args, **kwargs)

    def default_visit(self, node, *args, **kwargs):
        raise NotImplementedError('default_visit')


##


class Options:
    """Options to control how a Jmespath function is evaluated."""

    def __init__(
            self,
            dict_cls: type | None = None,
            custom_functions: Functions | None = None,
            enable_legacy_literals: bool = False,
    ) -> None:
        super().__init__()

        # The class to use when creating a dict.  The interpreter may create dictionaries during the evaluation of a
        # Jmespath expression.  For example, a multi-select hash will create a dictionary.  By default we use a dict()
        # type. You can set this value to change what dict type is used. The most common reason you would change this is
        # if you want to set a collections.OrderedDict so that you can have predictable key ordering.
        self.dict_cls = dict_cls
        self.custom_functions = custom_functions

        # The flag to enable pre-JEP-12 literal compatibility.
        # JEP-12 deprecates `foo` -> "foo" syntax.
        # Valid expressions MUST use: `"foo"` -> "foo"
        # Setting this flag to `True` enables support for legacy syntax.
        self.enable_legacy_literals = enable_legacy_literals


class _Expression:
    def __init__(self, expression: Node, interpreter: 'TreeInterpreter'):
        super().__init__()
        self.expression = expression
        self.interpreter = interpreter

    def visit(self, node, *args, **kwargs):
        return self.interpreter.visit(node, *args, **kwargs)


class TreeInterpreter(Visitor):
    COMPARATOR_FUNC: ta.Mapping[str, ta.Callable] = {
        'eq': _equals,
        'ne': lambda x, y: not _equals(x, y),
        'lt': operator.lt,
        'gt': operator.gt,
        'lte': operator.le,
        'gte': operator.ge,
    }

    _EQUALITY_OPS: ta.Sequence[str] = ['eq', 'ne']

    _ARITHMETIC_UNARY_FUNC: ta.Mapping[str, ta.Callable] = {
        'minus': operator.neg,
        'plus': lambda x: x,
    }

    _ARITHMETIC_FUNC: ta.Mapping[str, ta.Callable] = {
        'div': operator.floordiv,
        'divide': operator.truediv,
        'minus': operator.sub,
        'modulo': operator.mod,
        'multiply': operator.mul,
        'plus': operator.add,
    }

    def __init__(self, options: Options | None = None) -> None:
        super().__init__()

        self._dict_cls: type = dict

        if options is None:
            options = Options()
        self._options = options

        if options.dict_cls is not None:
            self._dict_cls = options.dict_cls

        if options.custom_functions is not None:
            self._functions: Functions = options.custom_functions
        else:
            self._functions = DefaultFunctions()

        self._root: Node | None = None
        self._scope: ScopedChainDict = ScopedChainDict()

    def default_visit(self, node: Node, *args: ta.Any, **kwargs: ta.Any) -> ta.NoReturn:
        raise NotImplementedError(node['type'])

    def evaluate(self, ast: Node, root: Node) -> ta.Any:
        self._root = root
        return self.visit(ast, root)

    def visit_subexpression(self, node: Node, value: ta.Any) -> ta.Any:
        result = value
        for child in node['children']:
            result = self.visit(child, result)
            if result is None:
                return None
        return result

    def visit_field(self, node: Node, value: ta.Any) -> ta.Any:
        try:
            return value.get(node['value'])
        except AttributeError:
            return None

    def visit_comparator(self, node: Node, value: ta.Any) -> ta.Any:
        # Common case: comparator is == or !=
        comparator_func = self.COMPARATOR_FUNC[node['value']]
        if node['value'] in self._EQUALITY_OPS:
            return comparator_func(
                self.visit(node['children'][0], value),
                self.visit(node['children'][1], value),
            )

        else:
            # Ordering operators are only valid for numbers. Evaluating any other type with a comparison operator will
            # yield a None value.
            left = self.visit(node['children'][0], value)
            right = self.visit(node['children'][1], value)
            # num_types = (int, float)
            if not (_is_comparable(left) and _is_comparable(right)):
                return None
            return comparator_func(left, right)

    def visit_arithmetic_unary(self, node: Node, value: ta.Any) -> ta.Any:
        operation = self._ARITHMETIC_UNARY_FUNC[node['value']]
        return operation(
            self.visit(node['children'][0], value),
        )

    def visit_arithmetic(self, node: Node, value: ta.Any) -> ta.Any:
        operation = self._ARITHMETIC_FUNC[node['value']]
        return operation(
            self.visit(node['children'][0], value),
            self.visit(node['children'][1], value),
        )

    def visit_current(self, node: Node, value: ta.Any) -> ta.Any:
        return value

    def visit_root(self, node: Node, value: ta.Any):
        return self._root

    def visit_expref(self, node: Node, value: ta.Any):
        return _Expression(node['children'][0], self)

    def visit_function_expression(self, node: Node, value: ta.Any):
        resolved_args = []
        for child in node['children']:
            current = self.visit(child, value)
            resolved_args.append(current)

        return self._functions.call_function(node['value'], resolved_args)

    def visit_filter_projection(self, node: Node, value: ta.Any):
        base = self.visit(node['children'][0], value)
        if not isinstance(base, list):
            return None

        comparator_node = node['children'][2]
        collected = []
        for element in base:
            if self._is_true(self.visit(comparator_node, element)):
                current = self.visit(node['children'][1], element)
                if current is not None:
                    collected.append(current)

        return collected

    def visit_flatten(self, node: Node, value: ta.Any):
        base = self.visit(node['children'][0], value)
        if not isinstance(base, list):
            # Can't flatten the object if it's not a list.
            return None

        merged_list = []
        for element in base:
            if isinstance(element, list):
                merged_list.extend(element)
            else:
                merged_list.append(element)

        return merged_list

    def visit_identity(self, node: Node, value: ta.Any):
        return value

    def visit_index(self, node: Node, value: ta.Any):
        # Even though we can index strings, we don't want to support that.
        if not isinstance(value, list):
            return None

        try:
            return value[node['value']]
        except IndexError:
            return None

    def visit_index_expression(self, node: Node, value: ta.Any):
        result = value
        for child in node['children']:
            result = self.visit(child, result)

        return result

    def visit_slice(self, node: Node, value: ta.Any):
        if isinstance(value, str):
            start, end, step = node['value']
            return value[start:end:step]

        if not isinstance(value, list):
            return None

        s = slice(*node['value'])
        return value[s]

    def visit_key_val_pair(self, node: Node, value: ta.Any):
        return self.visit(node['children'][0], value)

    def visit_literal(self, node: Node, value: ta.Any):
        return node['value']

    def visit_multi_select_dict(self, node: Node, value: ta.Any):
        collected = self._dict_cls()
        for child in node['children']:
            collected[child['value']] = self.visit(child, value)

        return collected

    def visit_multi_select_list(self, node: Node, value: ta.Any):
        collected = []
        for child in node['children']:
            collected.append(self.visit(child, value))

        return collected

    def visit_or_expression(self, node: Node, value: ta.Any):
        matched = self.visit(node['children'][0], value)

        if self._is_false(matched):
            matched = self.visit(node['children'][1], value)

        return matched

    def visit_and_expression(self, node: Node, value: ta.Any):
        matched = self.visit(node['children'][0], value)

        if self._is_false(matched):
            return matched

        return self.visit(node['children'][1], value)

    def visit_not_expression(self, node: Node, value: ta.Any):
        original_result = self.visit(node['children'][0], value)

        if _is_actual_number(original_result) and original_result == 0:
            # Special case for 0, !0 should be false, not true. 0 is not a special cased integer in jmespath.
            return False

        return not original_result

    def visit_pipe(self, node: Node, value: ta.Any):
        result = value
        for child in node['children']:
            result = self.visit(child, result)
        return result

    def visit_projection(self, node: Node, value: ta.Any):
        base = self.visit(node['children'][0], value)

        allow_string = False
        first_child = node['children'][0]
        if first_child['type'] == 'index_expression':
            nested_children = first_child['children']
            if len(nested_children) > 1 and nested_children[1]['type'] == 'slice':
                allow_string = True

        if isinstance(base, str) and allow_string:
            # projections are really sub-expressions in disguise evaluate the rhs when lhs is a sliced string
            return self.visit(node['children'][1], base)

        if not isinstance(base, list):
            return None
        collected = []
        for element in base:
            current = self.visit(node['children'][1], element)
            if current is not None:
                collected.append(current)

        return collected

    def visit_let_expression(self, node: Node, value: ta.Any):
        *bindings, expr = node['children']
        scope = {}
        for assign in bindings:
            scope.update(self.visit(assign, value))
        self._scope.push_scope(scope)
        result = self.visit(expr, value)
        self._scope.pop_scope()
        return result

    def visit_assign(self, node: Node, value: ta.Any):
        name = node['value']
        value = self.visit(node['children'][0], value)
        return {name: value}

    def visit_variable_ref(self, node: Node, value: ta.Any):
        try:
            return self._scope[node['value']]
        except KeyError:
            raise UndefinedVariableError(node['value'])  # noqa

    def visit_value_projection(self, node: Node, value: ta.Any):
        base = self.visit(node['children'][0], value)
        try:
            base = base.values()
        except AttributeError:
            return None

        collected = []
        for element in base:
            current = self.visit(node['children'][1], element)
            if current is not None:
                collected.append(current)

        return collected

    def _is_false(self, value: ta.Any) -> bool:
        # This looks weird, but we're explicitly using equality checks because the truth/false values are different
        # between python and jmespath.
        return (
            value == '' or  # noqa
            value == [] or
            value == {} or
            value is None or
            value is False
        )

    def _is_true(self, value: ta.Any) -> bool:
        return not self._is_false(value)


class GraphvizVisitor:
    def __init__(self) -> None:
        super().__init__()
        self._lines: list[str] = []
        self._count = 1

    def visit(self, node: Node):
        self._lines.append('digraph AST {')
        current = f"{node['type']}{self._count}"
        self._count += 1
        self._visit(node, current)
        self._lines.append('}')
        return '\n'.join(self._lines)

    def _visit(self, node: Node, current: ta.Any) -> None:
        self._lines.append('%s [label="%s(%s)"]' % (current, node['type'], node.get('value', '')))  # noqa
        for child in node.get('children', []):
            child_name = f"{child['type']}{self._count}"
            self._count += 1
            self._lines.append(f'  {current} -> {child_name}')
            self._visit(child, child_name)
