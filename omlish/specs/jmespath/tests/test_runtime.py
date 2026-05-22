import collections
import unittest

from .... import check
from ... import jmespath
from ..runtime import PythonRuntime


class AttrRuntime(PythonRuntime):
    def get_field(self, value, name):
        field = super().get_field(value, name)
        if field is not None:
            return field
        return getattr(value, name, None)


class AttrObject:
    def __init__(self, **kwargs):
        super().__init__()

        self.__dict__.update(kwargs)


class TestPythonRuntime(unittest.TestCase):
    def test_type_of(self):
        runtime = PythonRuntime()

        self.assertEqual(runtime.type_of(True), 'boolean')
        self.assertEqual(runtime.type_of([]), 'array')
        self.assertEqual(runtime.type_of({}), 'object')
        self.assertEqual(runtime.type_of(None), 'null')
        self.assertEqual(runtime.type_of('foo'), 'string')
        self.assertEqual(runtime.type_of(1), 'number')
        self.assertEqual(runtime.type_of(object()), 'unknown')

    def test_accessors_return_null_for_unsupported_values(self):
        runtime = PythonRuntime()

        self.assertIsNone(runtime.get_field([], 'foo'))
        self.assertIsNone(runtime.get_index({}, 0))
        self.assertIsNone(runtime.slice({}, None, None, None))
        self.assertIsNone(runtime.iter_array({}))
        self.assertIsNone(runtime.iter_object_values([]))
        self.assertIsNone(runtime.iter_object_items([]))

    def test_accessors_match_python_interpreter_semantics(self):
        runtime = PythonRuntime()

        self.assertEqual(runtime.get_field({'foo': 'bar'}, 'foo'), 'bar')
        self.assertEqual(runtime.get_index(['a', 'b'], -1), 'b')
        self.assertEqual(runtime.slice(['a', 'b', 'c'], 0, 2, None), ['a', 'b'])
        self.assertEqual(runtime.slice('abc', 0, 2, None), 'ab')
        self.assertEqual(list(check.not_none(runtime.iter_array(['a', 'b']))), ['a', 'b'])
        self.assertEqual(list(check.not_none(runtime.iter_object_values({'a': 1, 'b': 2}))), [1, 2])
        self.assertEqual(list(check.not_none(runtime.iter_object_items({'a': 1, 'b': 2}))), [('a', 1), ('b', 2)])

    def test_make_object_uses_dict_cls(self):
        runtime = PythonRuntime(collections.OrderedDict)

        obj = runtime.make_object({'a': 1, 'b': 2})

        self.assertIsInstance(obj, collections.OrderedDict)
        self.assertEqual(list(obj.items()), [('a', 1), ('b', 2)])

    def test_compare_matches_current_edge_cases(self):
        runtime = PythonRuntime()

        self.assertFalse(runtime.compare('eq', 1, True))
        self.assertTrue(runtime.compare('ne', 1, True))
        self.assertIsNone(runtime.compare('lt', [], 1))
        self.assertTrue(runtime.compare('lt', '2016', '2017'))

    def test_truthiness_matches_current_interpreter_semantics(self):
        runtime = PythonRuntime()

        false_values: list[object] = ['', [], {}, None, False]
        for value in false_values:
            self.assertTrue(runtime.is_false(value))
            self.assertFalse(runtime.is_true(value))

        true_values: list[object] = [0, 1, [None], {'a': None}, True]
        for value in true_values:
            self.assertFalse(runtime.is_false(value))
            self.assertTrue(runtime.is_true(value))


class TestTreeInterpreterRuntime(unittest.TestCase):
    def test_options_can_provide_runtime(self):
        obj = AttrObject(foo=AttrObject(bar='baz'))

        result = jmespath.search('foo.bar', obj, options=jmespath.Options(runtime=AttrRuntime()))

        self.assertEqual(result, 'baz')

    def test_functions_receive_python_values(self):
        obj = AttrObject(items=['a', 'b'])

        result = jmespath.search('length(items)', obj, options=jmespath.Options(runtime=AttrRuntime()))

        self.assertEqual(result, 2)
