# ruff: noqa: PT009
import unittest

from ... import jmespath


class CustomFunctions(jmespath.functions.DefaultFunctions):
    @jmespath.functions.signature({'types': ['string', 'array', 'object', 'null']})
    def _func_length0(self, s):
        return 0 if s is None else len(s)


class BoxedArray:
    def __init__(self, values):
        super().__init__()

        self.values = values


class BoxedArrayRuntime(jmespath.PythonRuntime):
    def type_of(self, value):
        if isinstance(value, BoxedArray):
            return 'array'
        return super().type_of(value)

    def iter_array(self, value):
        if isinstance(value, BoxedArray):
            return value.values
        return super().iter_array(value)

    def to_python(self, value):
        if isinstance(value, BoxedArray):
            return value.values
        return super().to_python(value)


class ContextFunctions(jmespath.functions.DefaultFunctions):
    @jmespath.functions.signature({'types': ['array']}, pass_context=True)
    def _func_ctx_type(self, arg, *, ctx):
        return ctx.runtime.type_of(arg)

    @jmespath.functions.signature({'types': ['array']})
    def _func_arg_class(self, arg):
        return type(arg).__name__


class TestCustomFunctions(unittest.TestCase):
    def setUp(self):
        self.options = jmespath.Options(custom_functions=CustomFunctions())

    def test_null_to_nonetype(self):
        data = {'a': {'b': [1, 2, 3]}}

        self.assertEqual(jmespath.search('length0(a.b)', data, self.options), 3)
        self.assertEqual(jmespath.search('length0(a.c)', data, self.options), 0)


class TestRuntimeAwareFunctions(unittest.TestCase):
    def test_type_check_uses_runtime_type(self):
        options = jmespath.Options(
            custom_functions=ContextFunctions(),
            runtime=BoxedArrayRuntime(),
        )

        self.assertEqual(jmespath.search('length(@)', BoxedArray([1, 2, 3]), options), 3)

    def test_context_is_passed_as_required_keyword_only_argument(self):
        options = jmespath.Options(
            custom_functions=ContextFunctions(),
            runtime=BoxedArrayRuntime(),
        )

        self.assertEqual(jmespath.search('ctx_type(@)', BoxedArray([1, 2, 3]), options), 'array')

    def test_non_context_functions_receive_python_values(self):
        options = jmespath.Options(
            custom_functions=ContextFunctions(),
            runtime=BoxedArrayRuntime(),
        )

        self.assertEqual(jmespath.search('arg_class(@)', BoxedArray([1, 2, 3]), options), 'list')
