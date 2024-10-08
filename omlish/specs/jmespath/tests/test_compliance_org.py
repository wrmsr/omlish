# ruff: noqa: PT009
import json
import os
import pprint
import unittest

from ... import jmespath
from ..visitor import Options
from .test_lexer import suppress_deprecated_string_literals_warning


TEST_DIR = os.path.dirname(os.path.abspath(__file__))
JMESPATH_ORG_DIR = os.path.join(TEST_DIR, 'compliance_org')
LEGACY_OPTIONS = Options(dict_cls=dict, enable_legacy_literals=True)

EXCLUDED_TESTS = ['literal.json']


def _compliance_tests(requested_test_type):
    for full_path in _walk_files():
        if full_path.endswith('.json'):
            for idx, (given, test_type, test_data) in enumerate(load_cases(full_path)):
                t = test_data
                # Benchmark tests aren't run as part of the normal test suite, so we only care about 'result' and
                # 'error' test_types.
                if test_type == 'result' and test_type == requested_test_type:
                    yield (
                        given,
                        t['expression'],
                        t['result'],
                        os.path.basename(full_path),
                        idx,
                    )
                elif test_type == 'error' and test_type == requested_test_type:
                    yield (
                        given,
                        t['expression'],
                        t['error'],
                        os.path.basename(full_path),
                        idx,
                    )


def _is_valid_test_file(filename):
    if (
        filename.endswith('.json')
        and not filename.endswith('schema.json')
        and os.path.basename(filename) not in EXCLUDED_TESTS
    ):
        return True
    return False


def _walk_files():
    for dir in [JMESPATH_ORG_DIR]:  # noqa
        for root, _, filenames in os.walk(dir):
            for filename in filenames:
                if _is_valid_test_file(filename):
                    yield os.path.join(root, filename)


def load_cases(full_path):
    with open(full_path) as f:
        all_test_data = json.load(f)
    for test_data in all_test_data:
        given = test_data['given']
        for case in test_data['cases']:
            if 'result' in case:
                test_type = 'result'
            elif 'error' in case:
                test_type = 'error'
            elif 'bench' in case:
                test_type = 'bench'
            else:
                raise RuntimeError(f'Unknown test type: {json.dumps(case)}')
            yield (given, test_type, case)


class TestExpression(unittest.TestCase):
    def setUp(self):
        super().setUp()

        self.enterContext(suppress_deprecated_string_literals_warning())

    def test_expression(self):
        for given, expression, expected, filename, idx in _compliance_tests('result'):
            self._test_expression(given, expression, expected, filename, idx)

    def _test_expression(self, given, expression, expected, filename, idx):
        print(f'_test_expression: {filename}:{idx}: {expression}')

        try:
            (actual, parsed) = _search_expression(given, expression, filename)
        except ValueError as e:
            raise AssertionError(f'jmespath expression failed to compile: "{expression}", error: {e}"')  # noqa

        expected_repr = json.dumps(expected, indent=4)
        actual_repr = json.dumps(actual, indent=4)
        error_msg = (
            "\n\n  (%s) The expression '%s' was supposed to give:\n%s\n"  # noqa
            "Instead it matched:\n%s\nparsed as:\n%s\ngiven:\n%s"
            % (
                filename,
                expression,
                expected_repr,
                actual_repr,
                pprint.pformat(parsed.parsed),
                json.dumps(given, indent=4),
            )
        )
        error_msg = error_msg.replace(r'\n', '\n')
        self.assertEqual(actual, expected, error_msg)


class TestErrorExpression(unittest.TestCase):
    def setUp(self):
        super().setUp()

        self.enterContext(suppress_deprecated_string_literals_warning())

    def test_error_expression(self):
        for given, expression, error, filename, idx in _compliance_tests('error'):
            self._test_error_expression(given, expression, error, filename, idx)

    def _test_error_expression(self, given, expression, error, filename, idx):
        print(f'_test_error_expression: {filename}:{idx}: {expression}')

        if error not in (
            'syntax',
            'invalid-type',
            'unknown-function',
            'invalid-arity',
            'invalid-value',
        ):
            raise RuntimeError(f"Unknown error type '{error}'")

        try:
            (_, parsed) = _search_expression(given, expression, filename)

        except ValueError:
            # Test passes, it raised a parse error as expected.
            pass

        except Exception as e:  # noqa
            # Failure because an unexpected exception was raised.
            error_msg = (
                "\n\n  (%s) The expression '%s' was suppose to be a "  # noqa
                "syntax error, but it raised an unexpected error:\n\n%s"
                % (filename, expression, e)
            )
            error_msg = error_msg.replace(r'\n', '\n')
            raise AssertionError(error_msg)  # noqa

        else:
            error_msg = (
                "\n\n  (%s) The expression '%s' was suppose to be a "  # noqa
                "syntax error, but it successfully parsed as:\n\n%s"
                % (filename, expression, pprint.pformat(parsed.parsed))
            )
            error_msg = error_msg.replace(r'\n', '\n')
            raise AssertionError(error_msg)  # noqa


def _search_expression(given, expression, filename):
    options = LEGACY_OPTIONS

    parsed = jmespath.compile(expression, options=options)
    actual = parsed.search(given, options=options)
    return (actual, parsed)
