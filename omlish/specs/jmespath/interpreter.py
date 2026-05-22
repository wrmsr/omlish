import typing as ta

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
from .ast import TernaryOperator
from .ast import ValueProjection
from .ast import VariableRef
from .errors import UndefinedVariableError
from .functions import DefaultFunctions
from .functions import Functions
from .options import Options
from .runtime import PythonRuntime
from .scope import ScopedChainDict
from .visitor import Visitor
from .visitor import node_type


##


class _Expression:
    def __init__(self, expression: Node, interpreter: Interpreter) -> None:
        super().__init__()

        self.expression = expression
        self.interpreter = interpreter

    def visit(self, node: Node, *args: ta.Any, **kwargs: ta.Any) -> ta.Any:
        return self.interpreter.visit(node, *args, **kwargs)


class Interpreter(Visitor):
    def __init__(self, options: Options | None = None) -> None:
        super().__init__()

        if options is None:
            options = Options()
        self._options = options

        if options.runtime is not None:
            self._runtime = options.runtime
        else:
            self._runtime = PythonRuntime(options.dict_cls)

        if options.custom_functions is not None:
            self._functions: Functions = options.custom_functions
        else:
            self._functions = DefaultFunctions()

        self._root: ta.Any = None
        self._scope: ScopedChainDict[str, ta.Any] = ScopedChainDict()

    def default_visit(self, node: Node, *args: ta.Any, **kwargs: ta.Any) -> ta.NoReturn:
        raise NotImplementedError(node_type(node))

    def evaluate(self, ast: Node, root: ta.Any) -> ta.Any:
        self._root = root
        return self.visit(ast, root)

    def visit_subexpression(self, node: Subexpression, value: ta.Any) -> ta.Any:
        result = value
        for child in node.children_nodes:
            result = self.visit(child, result)
            if self._runtime.is_null(result):
                return self._runtime.make_null()
        return result

    def visit_field(self, node: Field, value: ta.Any) -> ta.Any:
        return self._runtime.get_field(value, node.name)

    def visit_comparator(self, node: Comparator, value: ta.Any) -> ta.Any:
        return self._runtime.compare(
            node.name,
            self.visit(node.first, value),
            self.visit(node.second, value),
        )

    def visit_arithmetic_unary(self, node: ArithmeticUnary, value: ta.Any) -> ta.Any:
        return self._runtime.arithmetic_unary(
            node.operator,
            self.visit(node.expression, value),
        )

    def visit_arithmetic(self, node: Arithmetic, value: ta.Any) -> ta.Any:
        return self._runtime.arithmetic(
            node.operator,
            self.visit(node.left, value),
            self.visit(node.right, value),
        )

    def visit_current_node(self, node: CurrentNode, value: ta.Any) -> ta.Any:
        return value

    def visit_root_node(self, node: RootNode, value: ta.Any) -> ta.Any:
        return self._root

    def visit_expref(self, node: Expref, value: ta.Any) -> ta.Any:
        return _Expression(node.expression, self)

    def visit_function_expression(self, node: FunctionExpression, value: ta.Any) -> ta.Any:
        resolved_args = []
        for child in node.args:
            current = self.visit(child, value)
            resolved_args.append(self._runtime.to_python(current))

        return self._functions.call_function(node.name, resolved_args)

    def visit_filter_projection(self, node: FilterProjection, value: ta.Any) -> ta.Any:
        base = self.visit(node.left, value)
        base_items = self._runtime.iter_array(base)
        if base_items is None:
            return self._runtime.make_null()

        comparator_node = node.comparator
        collected: list[ta.Any] = []
        for element in base_items:
            if self._runtime.is_true(self.visit(comparator_node, element)):
                current = self.visit(node.right, element)
                if not self._runtime.is_null(current):
                    collected.append(current)

        return self._runtime.make_array(collected)

    def visit_flatten(self, node: Flatten, value: ta.Any) -> ta.Any:
        base = self.visit(node.node, value)
        base_items = self._runtime.iter_array(base)
        if base_items is None:
            return self._runtime.make_null()

        merged_list: list[ta.Any] = []
        for element in base_items:
            nested_items = self._runtime.iter_array(element)
            if nested_items is not None:
                merged_list.extend(nested_items)
            else:
                merged_list.append(element)

        return self._runtime.make_array(merged_list)

    def visit_identity(self, node: Identity, value: ta.Any) -> ta.Any:
        return value

    def visit_index(self, node: Index, value: ta.Any) -> ta.Any:
        return self._runtime.get_index(value, node.index)

    def visit_index_expression(self, node: IndexExpression, value: ta.Any) -> ta.Any:
        result = value
        for child in node.nodes:
            result = self.visit(child, result)

        return result

    def visit_slice(self, node: Slice, value: ta.Any) -> ta.Any:
        return self._runtime.slice(value, node.start, node.end, node.step)

    def visit_key_val_pair(self, node: KeyValPair, value: ta.Any) -> ta.Any:
        return self.visit(node.node, value)

    def visit_literal(self, node: Literal, value: ta.Any) -> ta.Any:
        return node.literal_value

    def visit_multi_select_dict(self, node: MultiSelectDict, value: ta.Any) -> ta.Any:
        collected: dict[str, ta.Any] = {}
        for child in node.nodes:
            collected[child.key_name] = self.visit(child, value)

        return self._runtime.make_object(collected)

    def visit_multi_select_list(self, node: MultiSelectList, value: ta.Any) -> ta.Any:
        collected: list[ta.Any] = []
        for child in node.nodes:
            collected.append(self.visit(child, value))

        return self._runtime.make_array(collected)

    def visit_or_expression(self, node: OrExpression, value: ta.Any) -> ta.Any:
        matched = self.visit(node.left, value)

        if self._is_false(matched):
            matched = self.visit(node.right, value)

        return matched

    def visit_and_expression(self, node: AndExpression, value: ta.Any) -> ta.Any:
        matched = self.visit(node.left, value)

        if self._is_false(matched):
            return matched

        return self.visit(node.right, value)

    def visit_not_expression(self, node: NotExpression, value: ta.Any) -> ta.Any:
        original_result = self.visit(node.expr, value)

        if self._runtime.is_zero_number(original_result):
            # Special case for 0, !0 should be false, not true. 0 is not a special cased integer in jmespath.
            return self._runtime.make_bool(False)

        return self._runtime.make_bool(self._runtime.is_false(original_result))

    def visit_pipe(self, node: Pipe, value: ta.Any) -> ta.Any:
        result = value
        for child in [node.left, node.right]:
            result = self.visit(child, result)
        return result

    def visit_projection(self, node: Projection, value: ta.Any) -> ta.Any:
        base = self.visit(node.left, value)

        allow_string = False
        first_child = node.left
        if isinstance(first_child, IndexExpression):
            nested_children = first_child.nodes
            if len(nested_children) > 1 and isinstance(nested_children[1], Slice):
                allow_string = True

        if self._runtime.type_of(base) == 'string' and allow_string:
            # projections are really sub-expressions in disguise evaluate the rhs when lhs is a sliced string
            return self.visit(node.right, base)

        base_items = self._runtime.iter_array(base)
        if base_items is None:
            return self._runtime.make_null()

        collected: list[ta.Any] = []
        for element in base_items:
            current = self.visit(node.right, element)
            if not self._runtime.is_null(current):
                collected.append(current)

        return self._runtime.make_array(collected)

    def visit_let_expression(self, node: LetExpression, value: ta.Any) -> ta.Any:
        scope = {}
        for assign in node.bindings:
            scope.update(self.visit(assign, value))
        self._scope.push_scope(scope)
        try:
            return self.visit(node.expr, value)
        finally:
            self._scope.pop_scope()

    def visit_assign(self, node: Assign, value: ta.Any) -> ta.Any:
        name = node.name
        value = self.visit(node.expr, value)
        return {name: value}

    def visit_variable_ref(self, node: VariableRef, value: ta.Any) -> ta.Any:
        try:
            return self._scope[node.name]
        except KeyError:
            raise UndefinedVariableError(node.name)  # noqa

    def visit_ternary_operator(self, node: TernaryOperator, value: ta.Any) -> ta.Any:
        evaluation = self.visit(node.condition, value)

        if self._is_false(evaluation):
            return self.visit(node.if_falsy, value)
        else:
            return self.visit(node.if_truthy, value)

    def visit_value_projection(self, node: ValueProjection, value: ta.Any) -> ta.Any:
        base = self.visit(node.left, value)
        base_values = self._runtime.iter_object_values(base)
        if base_values is None:
            return self._runtime.make_null()

        collected: list[ta.Any] = []
        for element in base_values:
            current = self.visit(node.right, element)
            if not self._runtime.is_null(current):
                collected.append(current)

        return self._runtime.make_array(collected)

    def _is_false(self, value: ta.Any) -> bool:
        return self._runtime.is_false(value)

    def _is_true(self, value: ta.Any) -> bool:
        return self._runtime.is_true(value)
