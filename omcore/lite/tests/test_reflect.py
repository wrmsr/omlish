# ruff: noqa: PT009 UP007 UP045
import typing as ta
import unittest

from .. import reflect as rfl


FooLiteral = ta.Literal['a', 'b', 'c']


class TestReflect(unittest.TestCase):
    def test_is_generic_alias(self):
        self.assertTrue(rfl.is_generic_alias(ta.Sequence[int]))
        self.assertFalse(rfl.is_generic_alias(int))

    def test_is_union_alias(self):
        self.assertTrue(rfl.is_union_alias(ta.Union[int, str]))
        self.assertTrue(rfl.is_union_alias(ta.Optional[int]))
        self.assertFalse(rfl.is_union_alias(int))

    def test_is_optional_alias(self):
        self.assertTrue(rfl.is_optional_alias(ta.Optional[int]))
        self.assertIs(rfl.get_optional_alias_arg(ta.Optional[int]), int)
        self.assertFalse(rfl.is_optional_alias(int))

    def test_is_new_type(self):
        self.assertFalse(rfl.is_new_type(int))
        self.assertTrue(rfl.is_new_type(ta.NewType('Foo', int)))

    def test_literals(self):
        self.assertFalse(rfl.is_literal_type(int))
        self.assertTrue(rfl.is_literal_type(FooLiteral))
        self.assertEqual(set(rfl.get_literal_type_args(FooLiteral)), {'a', 'b', 'c'})
