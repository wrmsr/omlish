# ruff: noqa: PT009
import json
import os
import pprint
import unittest

from ... import jmespath


TEST_DIR = os.path.dirname(os.path.abspath(__file__))
COMPLIANCE_DIR = os.path.join(TEST_DIR, 'compliance')
LEGACY_DIR = os.path.join(TEST_DIR, 'legacy')
NOT_SPECIFIED = object()
OPTIONS = jmespath.Options()


def _compliance_tests(requested_test_type):
    for full_path in _walk_files():
        if full_path.endswith('.json'):
            for given, test_type, test_data in load_cases(full_path):
                t = test_data
                # Benchmark tests aren't run as part of the normal test suite, so we only care about 'result' and
                # 'error' test_types.
                if test_type == 'result' and test_type == requested_test_type:
                    yield (
                        given,
                        t['expression'],
                        t['result'],
                        os.path.basename(full_path),
                    )
                elif test_type == 'error' and test_type == requested_test_type:
                    yield (
                        given,
                        t['expression'],
                        t['error'],
                        os.path.basename(full_path),
                    )


def _walk_files():
    # Check for a shortcut when running the tests interactively. If a JMESPATH_TEST is defined, that file is used as the
    # only test to run.  Useful when doing feature development.
    single_file = os.environ.get('JMESPATH_TEST')
    if single_file is not None:
        yield os.path.abspath(single_file)
    else:
        for root, _, filenames in os.walk(TEST_DIR):
            for filename in filenames:
                yield os.path.join(root, filename)
        for root, _, filenames in os.walk(LEGACY_DIR):
            for filename in filenames:
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
    def _test_expression(self, given, expression, expected, filename):
        print(f'_test_expression: {expression}')

        try:
            parsed = jmespath.compile(expression)
        except ValueError as e:
            raise AssertionError(f'jmespath expression failed to compile: "{expression}", error: {e}"')  # noqa
        actual = parsed.search(given, options=OPTIONS)
        expected_repr = json.dumps(expected, indent=4)
        actual_repr = json.dumps(actual, indent=4)
        error_msg = (
            "\n\n  (%s) The expression '%s' was suppose to give:\n%s\n"  # noqa
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

    def test_expression(self):
        for given, expression, expected, filename in _compliance_tests('result'):
            self._test_expression(given, expression, expected, filename)


class TestErrorExpression(unittest.TestCase):
    def _test_error_expression(self, given, expression, error, filename):
        print(f'_test_error_expression: {expression}')

        if error not in (
                'syntax',
                'invalid-type',
                'unknown-function',
                'invalid-arity',
                'invalid-value',
        ):
            raise RuntimeError(f"Unknown error type '{error}'")

        try:
            parsed = jmespath.compile(expression)
            parsed.search(given)

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

    def test_error_expression(self):
        for given, expression, error, filename in _compliance_tests('error'):
            self._test_error_expression(given, expression, error, filename)
