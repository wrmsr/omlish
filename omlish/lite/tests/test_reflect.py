# ruff: noqa: PT009 UP007 UP045
import typing as ta
import unittest

from .. import reflect as rfl


FooLiteral = ta.Literal['a', 'b', 'c']


class TestReflect(unittest.TestCase):
    def test_is_optional_alias(self):
        self.assertTrue(rfl.is_union_alias(ta.Union[int, str]))
        self.assertTrue(rfl.is_union_alias(ta.Optional[int]))
        self.assertFalse(rfl.is_union_alias(int))

    def test_is_new_type(self):
        self.assertFalse(rfl.is_new_type(int))
        self.assertTrue(rfl.is_new_type(ta.NewType('Foo', int)))

    def test_literals(self):
        self.assertFalse(rfl.is_literal_type(int))
        self.assertTrue(rfl.is_literal_type(FooLiteral))
        self.assertEqual(set(rfl.get_literal_type_args(FooLiteral)), {'a', 'b', 'c'})
