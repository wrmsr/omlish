# ruff: noqa: PT027
import inspect
import unittest

from .. import exceptions
from .. import functions


class TestFunctionSignatures(unittest.TestCase):

    def setUp(self):
        self._functions = functions.Functions()

    def test_signature_with_monotype_argument(self):
        (function_name, signature) = self._make_test('_function_with_monotyped_arguments')
        self._functions._validate_arguments(['string'], signature, function_name)  # noqa
        self.assertRaises(
            exceptions.ArityError, lambda:
            self._functions._validate_arguments([], signature, function_name),  # noqa
        )

    def test_signature_with_optional_arguments(self):
        (function_name, signature) = self._make_test('_function_with_optional_arguments')
        self._functions._validate_arguments(['string'], signature, function_name)  # noqa
        self._functions._validate_arguments(['string', 42], signature, function_name)  # noqa
        self._functions._validate_arguments(['string', 43], signature, function_name)  # noqa
        self.assertRaises(
            exceptions.ArityError, lambda:
            self._functions._validate_arguments([], signature, function_name),  # noqa
        )
        self.assertRaises(
            exceptions.ArityError, lambda:
            self._functions._validate_arguments(['string', 42, 43, 44], signature, function_name),  # noqa
        )

    def test_signature_with_variadic_arguments(self):
        (function_name, signature) = self._make_test('_function_with_variadic_arguments')
        self._functions._validate_arguments(['string', 'text1'], signature, function_name)  # noqa
        self._functions._validate_arguments(['string', 'text1', 'text2'], signature, function_name)  # noqa
        self.assertRaises(
            exceptions.VariadicArityError, lambda:
            self._functions._validate_arguments(['string'], signature, function_name),  # noqa
        )

    def test_signature_with_empty_argument(self):
        (function_name, signature) = self._make_test('_function_with_empty_argument')
        self._functions._validate_arguments([], signature, function_name)  # noqa

    def test_signature_with_no_arguments(self):
        (function_name, signature) = self._make_test('_function_with_no_arguments')
        self._functions._validate_arguments([], signature, function_name)  # noqa

    def _make_test(self, func_name):
        for name, method in inspect.getmembers(TestFunctionSignatures, predicate=inspect.isfunction):
            print(name)
            if name != func_name:
                continue
            signature = getattr(method, 'signature', None)
            return (func_name, signature)
        return None

    # arg1 can only be of type 'string' this signature supports testing simplified syntax where 'type' is a string
    # instead of an array of strings
    @functions.signature({'type': 'string'})
    def _function_with_monotyped_arguments(self, arg1):
        return None

    @functions.signature({'type': 'string'}, {'type': 'string', 'variadic': True})
    def _function_with_variadic_arguments(self, arg1, *arguments):
        return None

    @functions.signature(
        {'type': 'string'},
        {'type': 'number', 'optional': True},
        {'type': 'number', 'optional': True},
    )
    def _function_with_optional_arguments(self, arg1, opt1, opt2):
        return None

    @functions.signature({})
    def _function_with_empty_argument(self):
        return None

    @functions.signature()
    def _function_with_no_arguments(self):
        return None


if __name__ == '__main__':
    unittest.main()
