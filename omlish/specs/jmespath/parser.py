"""
Top down operator precedence parser.

This is an implementation of Vaughan R. Pratt's "Top Down Operator Precedence" parser.
(http://dl.acm.org/citation.cfm?doid=512927.512931).

These are some additional resources that help explain the general idea behind a Pratt parser:

* http://effbot.org/zone/simple-top-down-parsing.htm
* http://javascript.crockford.com/tdop/tdop.html

A few notes on the implementation.

* All the nud/led tokens are on the Parser class itself, and are dispatched using getattr().  This keeps all the parsing
  logic contained to a single class.
* We use two passes through the data.  One to create a list of token, then one pass through the tokens to create the
  AST.  While the lexer actually yields tokens, we convert it to a list so we can easily implement two tokens of
  lookahead.  A previous implementation used a fixed circular buffer, but it was significantly slower.  Also, the
  average jmespath expression typically does not have a large amount of token so this is not an issue.  And
  interestingly enough, creating a token list first is actually faster than consuming from the token iterator one token
  at a time.
"""
import dataclasses as dc
import random
import typing as ta

from ... import check
from .ast import AndExpression
from .ast import Arithmetic
from .ast import ArithmeticOperator
from .ast import ArithmeticUnary
from .ast import Assign
from .ast import Comparator
from .ast import ComparatorName
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
from .ast import UnaryArithmeticOperator
from .ast import ValueProjection
from .ast import VariableRef
from .errors import IncompleteExpressionError
from .errors import LexerError
from .errors import ParseError
from .lexer import Lexer
from .lexer import Token
from .visitor import GraphvizVisitor
from .visitor import Options
from .visitor import TreeInterpreter


##


class Parser:
    BINDING_POWER: ta.Mapping[str, int] = {
        'eof': 0,
        'variable': 0,
        'assign': 0,
        'unquoted_identifier': 0,
        'quoted_identifier': 0,
        'literal': 0,
        'rbracket': 0,
        'rparen': 0,
        'comma': 0,
        'rbrace': 0,
        'number': 0,
        'current': 0,
        'root': 0,
        'expref': 0,
        'colon': 0,
        'pipe': 1,
        'question': 2,
        'or': 3,
        'and': 4,
        'eq': 5,
        'gt': 5,
        'lt': 5,
        'gte': 5,
        'lte': 5,
        'ne': 5,
        'minus': 6,
        'plus': 6,
        'div': 7,
        'divide': 7,
        'modulo': 7,
        'multiply': 7,
        'flatten': 9,
        # Everything above stops a projection.
        'star': 20,
        'filter': 21,
        'dot': 40,
        'not': 45,
        'lbrace': 50,
        'lbracket': 55,
        'lparen': 60,
    }

    # The maximum binding power for a token that can stop a projection.
    _PROJECTION_STOP = 10

    # The _MAX_SIZE most recent expressions are cached in _CACHE dict.
    _CACHE: ta.ClassVar[dict[str, 'ParsedResult']] = {}  # noqa
    _MAX_SIZE = 128

    def __init__(self, lookahead: int = 2) -> None:
        super().__init__()

        self._tokenizer: ta.Iterable[Token] | None = None
        self._tokens: list[Token | None] = [None] * lookahead
        self._buffer_size = lookahead
        self._index = 0

    def parse(self, expression: str, options: Options | None = None) -> 'ParsedResult':
        cached = self._CACHE.get(expression)
        if cached is not None:
            return cached

        parsed_result = self._do_parse(expression, options)

        self._CACHE[expression] = parsed_result
        if len(self._CACHE) > self._MAX_SIZE:
            self._free_cache_entries()

        return parsed_result

    def _do_parse(self, expression: str, options: Options | None = None) -> 'ParsedResult':
        try:
            return self._parse(expression, options)

        except LexerError as e:
            e.expression = expression
            raise

        except IncompleteExpressionError as e:
            e.set_expression(expression)
            raise

        except ParseError as e:
            e.expression = expression
            raise

    def _parse(self, expression: str, options: Options | None = None) -> 'ParsedResult':
        self._tokenizer = Lexer().tokenize(expression, options)
        self._tokens = list(self._tokenizer)
        self._index = 0

        parsed = self._expression(binding_power=0)

        if self._current_token() != 'eof':
            t = check.not_none(self._lookahead_token(0))
            raise ParseError(
                t['start'],
                t['value'],
                t['type'],
                f'Unexpected token: {t["value"]}',
            )

        return ParsedResult(expression, parsed)

    def _expression(self, binding_power: int = 0) -> Node:
        left_token = check.not_none(self._lookahead_token(0))

        self._advance()

        nud_function = getattr(
            self,
            f'_token_nud_{left_token["type"]}',
            self._error_nud_token,
        )

        left = nud_function(left_token)  # noqa

        current_token = self._current_token()
        while binding_power < self.BINDING_POWER[current_token]:
            led = getattr(
                self,
                f'_token_led_{current_token}',
                None,
            )
            if led is None:
                error_token = check.not_none(self._lookahead_token(0))
                self._error_led_token(error_token)

            else:
                self._advance()
                left = led(left)
                current_token = self._current_token()

        return left

    def _token_nud_literal(self, token: Token) -> Node:
        return Literal(token['value'])

    def _token_nud_variable(self, token: Token) -> Node:
        return VariableRef(token['value'][1:])

    def _token_nud_unquoted_identifier(self, token: Token) -> Node:
        if token['value'] == 'let' and self._current_token() == 'variable':
            return self._parse_let_expression()
        else:
            return Field(token['value'])

    def _parse_let_expression(self) -> Node:
        bindings = []
        while True:
            var_token = check.not_none(self._lookahead_token(0))
            # Strip off the '$'.
            varname = var_token['value'][1:]
            self._advance()
            self._match('assign')
            assign_expr = self._expression()
            bindings.append(Assign(varname, assign_expr))
            if self._is_in_keyword(check.not_none(self._lookahead_token(0))):
                self._advance()
                break
            else:
                self._match('comma')
        expr = self._expression()
        return LetExpression(bindings, expr)

    def _is_in_keyword(self, token: Token) -> bool:
        return (
            token['type'] == 'unquoted_identifier' and
            token['value'] == 'in'
        )

    def _token_nud_quoted_identifier(self, token: Token) -> Node:
        field = Field(token['value'])

        # You can't have a quoted identifier as a function name.
        if self._current_token() == 'lparen':
            t = check.not_none(self._lookahead_token(0))
            raise ParseError(
                0,
                t['value'],
                t['type'],
                'Quoted identifier not allowed for function names.',
            )

        return field

    def _token_nud_star(self, token: Token) -> Node:
        left = Identity()
        right: Node
        if self._current_token() == 'rbracket':
            right = Identity()
        else:
            right = self._parse_projection_rhs(self.BINDING_POWER['star'])
        return ValueProjection(left, right)

    def _token_nud_filter(self, token: Token) -> Node:
        return self._token_led_filter(Identity())

    def _token_nud_lbrace(self, token: Token) -> Node:
        return self._parse_multi_select_hash()

    def _token_nud_lparen(self, token: Token) -> Node:
        expression = self._expression()
        self._match('rparen')
        return expression

    def _token_nud_minus(self, token: Token) -> Node:
        return self._parse_arithmetic_unary(token)

    def _token_nud_plus(self, token: Token) -> Node:
        return self._parse_arithmetic_unary(token)

    def _token_nud_flatten(self, token: Token) -> Node:
        left = Flatten(Identity())
        right = self._parse_projection_rhs(
            self.BINDING_POWER['flatten'])
        return Projection(left, right)

    def _token_nud_not(self, token: Token) -> Node:
        expr = self._expression(self.BINDING_POWER['not'])
        return NotExpression(expr)

    def _token_nud_lbracket(self, token: Token) -> Node:
        if self._current_token() in ['number', 'colon']:
            right = self._parse_index_expression()
            # We could optimize this and remove the identity() node. We don't really need an index_expression node, we
            # can just use emit an index node here if we're not dealing with a slice.
            return self._project_if_slice(Identity(), right)

        elif self._current_token() == 'star' and self._lookahead(1) == 'rbracket':
            self._advance()
            self._advance()
            right = self._parse_projection_rhs(self.BINDING_POWER['star'])
            return Projection(Identity(), right)

        else:
            return self._parse_multi_select_list()

    def _parse_index_expression(self) -> Node:
        # We're here:
        # [<current>
        #  ^
        #  | current token
        if self._lookahead(0) == 'colon' or self._lookahead(1) == 'colon':
            return self._parse_slice_expression()

        else:
            # Parse the syntax [number]
            node = Index(check.not_none(self._lookahead_token(0))['value'])
            self._advance()
            self._match('rbracket')
            return node

    def _parse_slice_expression(self) -> Node:
        # [start:end:step]
        # Where start, end, and step are optional. The last colon is optional as well.
        parts = [None, None, None]
        index = 0
        current_token = self._current_token()
        while current_token != 'rbracket' and index < 3:  # noqa
            if current_token == 'colon':  # noqa
                index += 1
                if index == 3:
                    self._raise_parse_error_for_token(check.not_none(self._lookahead_token(0)), 'syntax error')
                self._advance()

            elif current_token == 'number':  # noqa
                parts[index] = check.not_none(self._lookahead_token(0))['value']
                self._advance()

            else:
                self._raise_parse_error_for_token(check.not_none(self._lookahead_token(0)), 'syntax error')

            current_token = self._current_token()

        self._match('rbracket')
        return Slice(*parts)

    def _token_nud_current(self, token: Token) -> Node:
        return CurrentNode()

    def _token_nud_root(self, token: Token) -> Node:
        return RootNode()

    def _token_nud_expref(self, token: Token) -> Node:
        expression = self._expression(self.BINDING_POWER['expref'])
        return Expref(expression)

    def _token_led_dot(self, left: Node) -> Node:
        if self._current_token() != 'star':
            right = self._parse_dot_rhs(self.BINDING_POWER['dot'])
            if isinstance(left, Subexpression):
                return dc.replace(left, children_nodes=[*left.children_nodes, right])

            else:
                return Subexpression([left, right])

        else:
            # We're creating a projection.
            self._advance()
            right = self._parse_projection_rhs(self.BINDING_POWER['dot'])
            return ValueProjection(left, right)

    def _token_led_pipe(self, left: Node) -> Node:
        right = self._expression(self.BINDING_POWER['pipe'])
        return Pipe(left, right)

    def _token_led_or(self, left: Node) -> Node:
        right = self._expression(self.BINDING_POWER['or'])
        return OrExpression(left, right)

    def _token_led_and(self, left: Node) -> Node:
        right = self._expression(self.BINDING_POWER['and'])
        return AndExpression(left, right)

    def _token_led_lparen(self, left: Node) -> Node:
        if not isinstance(left, Field):
            #  0 - first func arg or closing paren.
            # -1 - '(' token
            # -2 - invalid function "name".
            prev_t = check.not_none(self._lookahead_token(-2))
            raise ParseError(
                prev_t['start'],
                prev_t['value'],
                prev_t['type'],
                f"Invalid function name '{prev_t['value']}'",
            )

        name = left.name
        args = []
        while self._current_token() != 'rparen':
            expression = self._expression()
            if self._current_token() == 'comma':
                self._match('comma')
            args.append(expression)
        self._match('rparen')

        function_node = FunctionExpression(name, args)
        return function_node

    def _token_led_filter(self, left: Node) -> Node:
        # Filters are projections.
        condition = self._expression(0)
        self._match('rbracket')
        right: Node
        if self._current_token() == 'flatten':
            right = Identity()
        else:
            right = self._parse_projection_rhs(self.BINDING_POWER['filter'])
        return FilterProjection(left, right, condition)

    def _token_led_eq(self, left: Node) -> Node:
        return self._parse_comparator(left, 'eq')

    def _token_led_ne(self, left: Node) -> Node:
        return self._parse_comparator(left, 'ne')

    def _token_led_gt(self, left: Node) -> Node:
        return self._parse_comparator(left, 'gt')

    def _token_led_gte(self, left: Node) -> Node:
        return self._parse_comparator(left, 'gte')

    def _token_led_lt(self, left: Node) -> Node:
        return self._parse_comparator(left, 'lt')

    def _token_led_lte(self, left: Node) -> Node:
        return self._parse_comparator(left, 'lte')

    def _token_led_div(self, left: Node) -> Node:
        return self._parse_arithmetic(left, 'div')

    def _token_led_divide(self, left: Node) -> Node:
        return self._parse_arithmetic(left, 'divide')

    def _token_led_minus(self, left: Node) -> Node:
        return self._parse_arithmetic(left, 'minus')

    def _token_led_modulo(self, left: Node) -> Node:
        return self._parse_arithmetic(left, 'modulo')

    def _token_led_multiply(self, left: Node) -> Node:
        return self._parse_arithmetic(left, 'multiply')

    def _token_led_plus(self, left: Node) -> Node:
        return self._parse_arithmetic(left, 'plus')

    def _token_led_star(self, left: Node) -> Node:
        return self._parse_arithmetic(left, 'multiply')

    def _token_led_flatten(self, left: Node) -> Node:
        left = Flatten(left)
        right = self._parse_projection_rhs(self.BINDING_POWER['flatten'])
        return Projection(left, right)

    def _token_led_lbracket(self, left: Node) -> Node:
        token = check.not_none(self._lookahead_token(0))
        if token['type'] in ['number', 'colon']:
            right = self._parse_index_expression()
            if isinstance(left, IndexExpression):
                # Optimization: if the left node is an index expr, we can avoid creating another node and instead just
                # add the right node as a child of the left.
                return dc.replace(left, nodes=[*left.nodes, right])

            else:
                return self._project_if_slice(left, right)

        else:
            # We have a projection
            self._match('star')
            self._match('rbracket')
            right = self._parse_projection_rhs(self.BINDING_POWER['star'])
            return Projection(left, right)

    def _token_led_question(self, condition: Node) -> Node:
        left = self._expression()
        self._match('colon')
        right = self._expression()
        return TernaryOperator(condition, left, right)

    def _project_if_slice(self, left: Node, right: Node) -> Node:
        index_expr = IndexExpression([left, right])
        if isinstance(right, Slice):
            return Projection(
                index_expr,
                self._parse_projection_rhs(self.BINDING_POWER['star']),
            )
        else:
            return index_expr

    def _parse_comparator(self, left: Node, comparator: str) -> Node:
        right = self._expression(self.BINDING_POWER[comparator])
        return Comparator(ta.cast(ComparatorName, comparator), left, right)

    def _parse_arithmetic_unary(self, token: Token) -> Node:
        expression = self._expression(self.BINDING_POWER[token['type']])
        return ArithmeticUnary(ta.cast(UnaryArithmeticOperator, token['type']), expression)

    def _parse_arithmetic(self, left: Node, operator: str) -> Node:
        right = self._expression(self.BINDING_POWER[operator])
        return Arithmetic(ta.cast(ArithmeticOperator, operator), left, right)

    def _parse_multi_select_list(self) -> Node:
        expressions: list[Node] = []
        while True:
            expression = self._expression()
            expressions.append(expression)
            if self._current_token() == 'rbracket':
                break
            else:
                self._match('comma')
        self._match('rbracket')
        return MultiSelectList(expressions)

    def _parse_multi_select_hash(self) -> Node:
        pairs: list[KeyValPair] = []
        while True:
            key_token = check.not_none(self._lookahead_token(0))

            # Before getting the token value, verify it's an identifier.
            self._match_multiple_tokens(token_types=['quoted_identifier', 'unquoted_identifier'])
            key_name = key_token['value']

            self._match('colon')
            value = self._expression(0)

            node = KeyValPair(key_name=key_name, node=value)

            pairs.append(node)
            if self._current_token() == 'comma':
                self._match('comma')

            elif self._current_token() == 'rbrace':
                self._match('rbrace')
                break

        return MultiSelectDict(nodes=pairs)

    def _parse_projection_rhs(self, binding_power: int) -> Node:
        right: Node

        # Parse the right hand side of the projection.
        if self.BINDING_POWER[self._current_token()] < self._PROJECTION_STOP:
            # BP of 10 are all the tokens that stop a projection.
            right = Identity()

        elif self._current_token() == 'lbracket':
            right = self._expression(binding_power)

        elif self._current_token() == 'filter':
            right = self._expression(binding_power)

        elif self._current_token() == 'dot':
            self._match('dot')
            right = self._parse_dot_rhs(binding_power)

        else:
            self._raise_parse_error_for_token(check.not_none(self._lookahead_token(0)), 'syntax error')

        return right

    def _parse_dot_rhs(self, binding_power: int) -> Node:
        # From the grammar:
        # expression '.' ( identifier /
        #                  multi-select-list /
        #                  multi-select-hash /
        #                  function-expression /
        #                  *
        # In terms of tokens that means that after a '.', you can have:
        lookahead = self._current_token()

        # Common case "foo.bar", so first check for an identifier.
        if lookahead in ['quoted_identifier', 'unquoted_identifier', 'star']:
            return self._expression(binding_power)

        elif lookahead == 'lbracket':
            self._match('lbracket')
            return self._parse_multi_select_list()

        elif lookahead == 'lbrace':
            self._match('lbrace')
            return self._parse_multi_select_hash()

        else:
            t = check.not_none(self._lookahead_token(0))
            allowed = ['quoted_identifier', 'unquoted_identifier', 'lbracket', 'lbrace']
            msg = f'Expecting: {allowed}, got: {t["type"]}'
            self._raise_parse_error_for_token(t, msg)
            raise RuntimeError  # noqa

    def _error_nud_token(self, token: Token) -> ta.NoReturn:
        if token['type'] == 'eof':
            raise IncompleteExpressionError(
                token['start'],
                token['value'],
                token['type'],
            )

        self._raise_parse_error_for_token(token, 'invalid token')

    def _error_led_token(self, token: Token) -> ta.NoReturn:
        self._raise_parse_error_for_token(token, 'invalid token')

    def _match(self, token_type: str | None = None) -> None:
        # inline'd self._current_token()
        if self._current_token() == token_type:
            # inline'd self._advance()
            self._advance()
        else:
            self._raise_parse_error_maybe_eof(token_type, self._lookahead_token(0))

    def _match_multiple_tokens(self, token_types: ta.Container[str]) -> None:
        if self._current_token() not in token_types:
            self._raise_parse_error_maybe_eof(token_types, self._lookahead_token(0))
        self._advance()

    def _advance(self) -> None:
        self._index += 1

    def _current_token(self) -> str:
        return check.not_none(self._tokens[self._index])['type']

    def _lookahead(self, number: int) -> str:
        return check.not_none(self._tokens[self._index + number])['type']

    def _lookahead_token(self, number: int) -> Token | None:
        return self._tokens[self._index + number]

    def _raise_parse_error_for_token(self, token: Token, reason: str) -> ta.NoReturn:
        lex_position = token['start']
        actual_value = token['value']
        actual_type = token['type']
        raise ParseError(
            lex_position,
            actual_value,
            actual_type,
            reason,
        )

    def _raise_parse_error_maybe_eof(self, expected_type, token):
        lex_position = token['start']
        actual_value = token['value']
        actual_type = token['type']
        if actual_type == 'eof':
            raise IncompleteExpressionError(
                lex_position,
                actual_value,
                actual_type,
            )

        message = f'Expecting: {expected_type}, got: {actual_type}'
        raise ParseError(
            lex_position,
            actual_value,
            actual_type,
            message,
        )

    def _free_cache_entries(self):
        keys = list(self._CACHE.keys())
        for key in random.sample(keys, min(len(keys), int(self._MAX_SIZE / 2))):
            self._CACHE.pop(key, None)

    @classmethod
    def purge(cls) -> None:
        """Clear the expression compilation cache."""

        cls._CACHE.clear()


class ParsedResult:
    def __init__(self, expression: str, parsed: Node) -> None:
        super().__init__()

        self.expression = expression
        self.parsed = parsed

    def search(self, value: ta.Any, options: Options | None = None) -> ta.Any:
        evaluator = TreeInterpreter(options)
        return evaluator.evaluate(self.parsed, value)

    def _render_dot_file(self) -> str:
        """
        Render the parsed AST as a dot file.

        Note that this is marked as an internal method because the AST is an implementation detail and is subject to
        change.  This method can be used to help troubleshoot or for development purposes, but is not considered part of
        the public supported API.  Use at your own risk.
        """

        renderer = GraphvizVisitor()
        contents = renderer.visit(self.parsed)
        return contents

    def __repr__(self) -> str:
        return repr(self.parsed)


def compile(expression: str, options: Options | None = None) -> ParsedResult:  # noqa
    return Parser().parse(expression, options=options)


def search(expression: str, data: ta.Any, options: Options | None = None) -> ta.Any:
    return compile(expression, options).search(data, options=options)
