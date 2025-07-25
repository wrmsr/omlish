# ruff: noqa: PT009 PT027
import html
import random
import re
import string
import threading
import unittest

from .. import ast
from .. import errors
from .. import parser
from .. import visitor


class TestParser(unittest.TestCase):
    def setUp(self):
        self.parser = parser.Parser()

    def assert_parsed_ast(self, expression, expected_ast):
        parsed = self.parser.parse(expression)
        self.assertEqual(parsed.parsed, expected_ast)

    def test_parse_empty_string_raises_exception(self):
        with self.assertRaises(errors.EmptyExpressionError):
            self.parser.parse('')

    def test_field(self):
        self.assert_parsed_ast('foo', ast.Field('foo'))

    def test_dot_syntax(self):
        self.assert_parsed_ast(
            'foo.bar', ast.Subexpression([ast.Field('foo'), ast.Field('bar')]),
        )

    def test_multiple_dots(self):
        parsed = self.parser.parse('foo.bar.baz')
        self.assertEqual(parsed.search({'foo': {'bar': {'baz': 'correct'}}}), 'correct')

    def test_index(self):
        parsed = self.parser.parse('foo[1]')
        self.assertEqual(parsed.search({'foo': ['zero', 'one', 'two']}), 'one')

    def test_quoted_subexpression(self):
        self.assert_parsed_ast(
            '"foo"."bar"', ast.Subexpression([ast.Field('foo'), ast.Field('bar')]),
        )

    def test_wildcard(self):
        parsed = self.parser.parse('foo[*]')
        self.assertEqual(
            parsed.search({'foo': ['zero', 'one', 'two']}), ['zero', 'one', 'two'],
        )

    def test_wildcard_with_children(self):
        parsed = self.parser.parse('foo[*].bar')
        self.assertEqual(
            parsed.search({'foo': [{'bar': 'one'}, {'bar': 'two'}]}), ['one', 'two'],
        )

    def test_or_expression(self):
        parsed = self.parser.parse('foo || bar')
        self.assertEqual(parsed.search({'foo': 'foo'}), 'foo')
        self.assertEqual(parsed.search({'bar': 'bar'}), 'bar')
        self.assertEqual(parsed.search({'foo': 'foo', 'bar': 'bar'}), 'foo')
        self.assertEqual(parsed.search({'bad': 'bad'}), None)

    def test_complex_or_expression(self):
        parsed = self.parser.parse('foo.foo || foo.bar')
        self.assertEqual(parsed.search({'foo': {'foo': 'foo'}}), 'foo')
        self.assertEqual(parsed.search({'foo': {'bar': 'bar'}}), 'bar')
        self.assertEqual(parsed.search({'foo': {'baz': 'baz'}}), None)

    def test_or_repr(self):
        self.assert_parsed_ast(
            'foo || bar', ast.OrExpression(ast.Field('foo'), ast.Field('bar')),
        )

    def test_arithmetic_expressions(self):
        operations = {
            '+': 'plus',
            '-': 'minus',
            '//': 'div',
            '/': 'divide',
            '%': 'modulo',
            '\u2212': 'minus',
            '\u00d7': 'multiply',
            '\u00f7': 'divide',
        }
        for sign, operation in operations.items():
            expression = f'foo {sign} bar'
            self.assert_parsed_ast(
                expression,
                ast.Arithmetic(
                    operation,  # type: ignore
                    ast.Field('foo'),
                    ast.Field('bar'),
                ))

    def test_arithmetic_unary(self):
        operations = {
            '+': 'plus',
            '-': 'minus',
            '\u2212': 'minus',
        }
        for sign, operation in operations.items():
            expression = f'{sign} foo'
            self.assert_parsed_ast(
                expression,
                ast.ArithmeticUnary(
                    operation,  # type: ignore
                    ast.Field('foo'),
                ))

    def test_arithmetic_multiplication(self):
        self.assert_parsed_ast(
            'foo * bar',
            ast.Arithmetic(
                'multiply',
                ast.Field('foo'),
                ast.Field('bar'),
            ))

    def test_unicode_literals_escaped(self):
        self.assert_parsed_ast(r'`"\u2713"`', ast.Literal('\u2713'))

    def test_multiselect(self):
        parsed = self.parser.parse('foo.{bar: bar,baz: baz}')
        self.assertEqual(
            parsed.search({'foo': {'bar': 'bar', 'baz': 'baz', 'qux': 'qux'}}),
            {'bar': 'bar', 'baz': 'baz'},
        )

    def test_multiselect_subexpressions(self):
        parsed = self.parser.parse('foo.{"bar.baz": bar.baz, qux: qux}')
        self.assertEqual(
            parsed.search({'foo': {'bar': {'baz': 'CORRECT'}, 'qux': 'qux'}}),
            {'bar.baz': 'CORRECT', 'qux': 'qux'},
        )

    def test_multiselect_with_all_quoted_keys(self):
        parsed = self.parser.parse('foo.{"bar": bar.baz, "qux": qux}')
        result = parsed.search({'foo': {'bar': {'baz': 'CORRECT'}, 'qux': 'qux'}})
        self.assertEqual(result, {'bar': 'CORRECT', 'qux': 'qux'})

    def test_function_call_with_and_statement(self):
        self.assert_parsed_ast(
            'f(@ && @)',
            ast.FunctionExpression(
                'f',
                [
                    ast.AndExpression(
                        ast.CurrentNode(),
                        ast.CurrentNode(),
                    ),
                ],
            ),
        )

    def test_root_node(self):
        self.assert_parsed_ast(
            '$[0]',
            ast.IndexExpression(
                [
                    ast.RootNode(),
                    ast.Index(0),
                ],
            ),
        )


class TestErrorMessages(unittest.TestCase):
    def setUp(self):
        self.parser = parser.Parser()

    def assert_error_message(
        self, expression, error_message, exception=errors.ParseError,
    ):
        try:
            self.parser.parse(expression)
        except exception as e:
            self.assertEqual(error_message, str(e))
            return
        except Exception as e:  # noqa
            self.fail(
                f'Unexpected error raised ({e.__class__.__name__}: {e}) for bad expression: {expression}',
            )
        else:
            self.fail(f'ParseError not raised for bad expression: {expression}')

    def test_bad_parse(self):
        with self.assertRaises(errors.ParseError):
            self.parser.parse('foo]baz')

    def test_bad_parse_error_message(self):
        error_message = (
            'Unexpected token: ]: Parse error at column 3, '
            'token "]" (RBRACKET), for expression:\n'
            '"foo]baz"\n'
            '    ^'
        )
        self.assert_error_message('foo]baz', error_message)

    def test_bad_parse_error_message_with_multiselect(self):
        error_message = (
            'Invalid jmespath expression: Incomplete expression:\n'
            '"foo.{bar: baz,bar: bar"\n'
            '                       ^'
        )
        self.assert_error_message('foo.{bar: baz,bar: bar', error_message)

    def test_incomplete_expression_with_missing_paren(self):
        error_message = (
            'Invalid jmespath expression: Incomplete expression:\n'
            '"length(@,"\n'
            '          ^'
        )
        self.assert_error_message('length(@,', error_message)

    def test_bad_lexer_values(self):
        error_message = (
            'Bad jmespath expression: Unclosed " delimiter:\nfoo."bar\n    ^'
        )
        self.assert_error_message(
            'foo."bar', error_message, exception=errors.LexerError,
        )

    def test_bad_unicode_string(self):
        # This error message is straight from the JSON parser and pypy has a slightly different error message, so we're
        # not using assert_error_message.
        error_message = re.compile(
            r'Bad jmespath expression: Invalid \\uXXXX escape.*\\uAZ12', re.DOTALL,
        )
        with self.assertRaisesRegex(errors.LexerError, error_message):
            self.parser.parse(r'"\uAZ12"')


class TestParserWildcards(unittest.TestCase):
    def setUp(self):
        self.parser = parser.Parser()
        self.data = {
            'foo': [
                {'bar': [{'baz': 'one'}, {'baz': 'two'}]},
                {'bar': [{'baz': 'three'}, {'baz': 'four'}, {'baz': 'five'}]},
            ],
        }

    def test_multiple_index_wildcards(self):
        parsed = self.parser.parse('foo[*].bar[*].baz')
        self.assertEqual(
            parsed.search(self.data), [['one', 'two'], ['three', 'four', 'five']],
        )

    def test_wildcard_mix_with_indices(self):
        parsed = self.parser.parse('foo[*].bar[0].baz')
        self.assertEqual(parsed.search(self.data), ['one', 'three'])

    def test_wildcard_mix_last(self):
        parsed = self.parser.parse('foo[0].bar[*].baz')
        self.assertEqual(parsed.search(self.data), ['one', 'two'])

    def test_indices_out_of_bounds(self):
        parsed = self.parser.parse('foo[*].bar[2].baz')
        self.assertEqual(parsed.search(self.data), ['five'])

    def test_root_indices(self):
        parsed = self.parser.parse('[0]')
        self.assertEqual(parsed.search(['one', 'two']), 'one')

    def test_root_wildcard(self):
        parsed = self.parser.parse('*.foo')
        data = {
            'top1': {'foo': 'bar'},
            'top2': {'foo': 'baz'},
            'top3': {'notfoo': 'notfoo'},
        }
        # Sorted is being used because the order of the keys are not required to be in any specific order.
        self.assertEqual(sorted(parsed.search(data)), sorted(['bar', 'baz']))
        self.assertEqual(
            sorted(self.parser.parse('*.notfoo').search(data)), sorted(['notfoo']),
        )

    def test_only_wildcard(self):
        parsed = self.parser.parse('*')
        data = {'foo': 'a', 'bar': 'b', 'baz': 'c'}
        self.assertEqual(sorted(parsed.search(data)), sorted(['a', 'b', 'c']))

    def test_escape_sequences(self):
        self.assertEqual(
            self.parser.parse(r'"foo\tbar"').search({'foo\tbar': 'baz'}), 'baz',
        )
        self.assertEqual(
            self.parser.parse(r'"foo\nbar"').search({'foo\nbar': 'baz'}), 'baz',
        )
        self.assertEqual(
            self.parser.parse(r'"foo\bbar"').search({'foo\bbar': 'baz'}), 'baz',
        )
        self.assertEqual(
            self.parser.parse(r'"foo\fbar"').search({'foo\fbar': 'baz'}), 'baz',
        )
        self.assertEqual(
            self.parser.parse(r'"foo\rbar"').search({'foo\rbar': 'baz'}), 'baz',
        )

    def test_consecutive_escape_sequences(self):
        parsed = self.parser.parse(r'"foo\\nbar"')
        self.assertEqual(parsed.search({'foo\\nbar': 'baz'}), 'baz')

        parsed = self.parser.parse(r'"foo\n\t\rbar"')
        self.assertEqual(parsed.search({'foo\n\t\rbar': 'baz'}), 'baz')

    def test_escape_sequence_at_end_of_string_not_allowed(self):
        with self.assertRaises(ValueError):
            self.parser.parse('foobar\\')

    def test_wildcard_with_multiselect(self):
        parsed = self.parser.parse('foo.*.{a: a, b: b}')
        data = {
            'foo': {
                'one': {
                    'a': {'c': 'CORRECT', 'd': 'other'},
                    'b': {'c': 'ALSOCORRECT', 'd': 'other'},
                },
                'two': {
                    'a': {'c': 'CORRECT', 'd': 'other'},
                    'c': {'c': 'WRONG', 'd': 'other'},
                },
            },
        }
        match = parsed.search(data)
        self.assertEqual(len(match), 2)
        self.assertIn('a', match[0])
        self.assertIn('b', match[0])
        self.assertIn('a', match[1])
        self.assertIn('b', match[1])


class TestMergedLists(unittest.TestCase):
    def setUp(self):
        self.parser = parser.Parser()
        self.data = {
            'foo': [
                [['one', 'two'], ['three', 'four']],
                [['five', 'six'], ['seven', 'eight']],
                [['nine'], ['ten']],
            ],
        }

    def test_merge_with_indices(self):
        parsed = self.parser.parse('foo[][0]')
        match = parsed.search(self.data)
        self.assertEqual(match, ['one', 'three', 'five', 'seven', 'nine', 'ten'])

    def test_trailing_merged_operator(self):
        parsed = self.parser.parse('foo[]')
        match = parsed.search(self.data)
        self.assertEqual(
            match,
            [
                ['one', 'two'],
                ['three', 'four'],
                ['five', 'six'],
                ['seven', 'eight'],
                ['nine'],
                ['ten'],
            ],
        )


class TestTernaryOperatorExpressions(unittest.TestCase):
    def setUp(self):
        self.parser = parser.Parser()
        self.data = {
            'true': True,
            'false': False,
            'foo': 'foo',
            'bar': 'bar',
            'baz': 'baz',
            'qux': 'qux',
            'quux': 'quux',
        }

    def test_ternary_operator_expression(self):
        parsed = self.parser.parse('true ? foo : bar')
        match = parsed.search(self.data)
        self.assertEqual(match, 'foo')

    def test_nested_ternary_operator_expressions(self):
        parsed = self.parser.parse('foo ? bar ? baz : qux : quux')
        match = parsed.search(self.data)
        self.assertEqual(match, 'baz')


class TestParserCaching(unittest.TestCase):
    def test_compile_lots_of_expressions(self):
        # We have to be careful here because this is an implementation detail that should be abstracted from the user,
        # but we need to make sure we exercise the code and that it doesn't blow up.
        p = parser.Parser()
        compiled = []
        compiled2 = []
        for i in range(parser.Parser._MAX_SIZE + 1):  # noqa
            compiled.append(p.parse(f'foo{i}'))
        # Rerun the test and half of these entries should be from the cache but they should still be equal to compiled.
        for i in range(parser.Parser._MAX_SIZE + 1):  # noqa
            compiled2.append(p.parse(f'foo{i}'))
        self.assertEqual(len(compiled), len(compiled2))
        self.assertEqual(
            [expr.parsed for expr in compiled], [expr.parsed for expr in compiled2],
        )

    def test_cache_purge(self):
        p = parser.Parser()
        first = p.parse('foo')
        cached = p.parse('foo')
        p.purge()
        second = p.parse('foo')
        self.assertEqual(first.parsed, second.parsed)
        self.assertEqual(first.parsed, cached.parsed)

    def test_thread_safety_of_cache(self):
        errors = []
        expressions = [
            ''.join(random.choice(string.ascii_letters) for _ in range(3))
            for _ in range(2000)
        ]

        def worker():
            p = parser.Parser()
            for expression in expressions:
                try:
                    p.parse(expression)
                except Exception as e:  # noqa
                    errors.append(e)

        threads = []
        for _ in range(10):
            threads.append(threading.Thread(target=worker))
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        self.assertEqual(errors, [])


class TestParserAddsExpressionAttribute(unittest.TestCase):
    def test_expression_available_from_parser(self):
        p = parser.Parser()
        parsed = p.parse('foo.bar')
        self.assertEqual(parsed.expression, 'foo.bar')


class TestParsedResultAddsOptions(unittest.TestCase):
    def test_can_have_ordered_dict(self):
        p = parser.Parser()
        parsed = p.parse('{a: a, b: b, c: c}')
        options = visitor.Options()
        result = parsed.search({'c': 'c', 'b': 'b', 'a': 'a'}, options=options)
        self.assertEqual(list(result), ['a', 'b', 'c'])


Q = html.escape('"')


class TestRenderGraphvizFile(unittest.TestCase):
    def test_dot_file_rendered(self):
        p = parser.Parser()
        result = p.parse('foo')
        dot_contents = result._render_dot_file()  # noqa
        self.assertEqual(dot_contents, f'digraph AST {{\nfield1 [label="field({Q}foo{Q})"]\n}}')

    def test_dot_file_subexpr(self):
        p = parser.Parser()
        result = p.parse('foo.bar')
        dot_contents = result._render_dot_file()  # noqa
        self.assertEqual(
            dot_contents,
            'digraph AST {\n'
            'subexpression1 [label="subexpression()"]\n'
            '  subexpression1 -> field2\n'
            f'field2 [label="field({Q}foo{Q})"]\n'
            '  subexpression1 -> field3\n'
            f'field3 [label="field({Q}bar{Q})"]\n}}',
        )


if __name__ == '__main__':
    unittest.main()
