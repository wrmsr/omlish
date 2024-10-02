# ruff: noqa: PT009
import json
import os
import pprint
import unittest

from ... import jmespath
from ....diag import pydevd


TEST_DIR = os.path.dirname(os.path.abspath(__file__))
COMPLIANCE_DIR = os.path.join(TEST_DIR, 'compliance')
LEGACY_DIR = os.path.join(TEST_DIR, 'legacy')
NOT_SPECIFIED = object()
COMPLIANCE_OPTIONS = jmespath.Options(dict_cls=dict)
LEGACY_OPTIONS = jmespath.Options(dict_cls=dict, enable_legacy_literals=True)


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


def _walk_files():
    # Check for a shortcut when running the tests interactively. If a JMESPATH_TEST is defined, that file is used as the
    # only test to run.  Useful when doing feature development.
    single_file = os.environ.get('JMESPATH_TEST')
    if single_file is not None:
        yield os.path.abspath(single_file)
    else:
        for dir in [COMPLIANCE_DIR, LEGACY_DIR]:
            for root, dirnames, filenames in os.walk(dir):
                for filename in filenames:
                    if filename.endswith('.json') and not filename.endswith('schema.json'):
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
    def test_expression(self):
        for given, expression, expected, filename, idx in _compliance_tests('result'):
            self._test_expression(given, expression, expected, filename, idx)

    def _test_expression(self, given, expression, expected, filename, idx):
        print(f'_test_expression: {filename}:{idx}: {expression}')

        # if (filename, idx) != ('slice.json', 41):
        #     return

        try:
            (actual, parsed) = _search_expression(given, expression, filename)
        except ValueError as e:
            if pydevd.is_present():
                raise
            raise AssertionError(f'jmespath expression failed to compile: "{expression}", error: {e}"') from e  # noqa

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
    def test_error_expression(self):
        for given, expression, error, filename, idx in _compliance_tests('error'):
            self._test_error_expression(given, expression, error, filename, idx)

    def _test_error_expression(self, given, expression, error, filename, idx):
        print(f'_test_error_expression: {filename}:{idx}: {expression}')

        if error not in (
                'syntax',
                'invalid-type',
                'undefined-variable',
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
    options = LEGACY_OPTIONS if filename.startswith('legacy') else COMPLIANCE_OPTIONS

    # This test suite contains identical expressions tested against both a legacy and a JEP-12 standards-compliant
    # parser.

    # However, the Parser() class contains a cache of compiled expressions for performance purposes

    # To prevent conflicts between legacy and JEP-12 standards-compliant evaluation, we need to clear the cache here

    jmespath.parser.Parser()._free_cache_entries()  # noqa

    parsed = jmespath.compile(expression, options=options)
    actual = parsed.search(given, options=options)
    return actual, parsed
