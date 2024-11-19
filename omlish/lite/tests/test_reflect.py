# ruff: noqa: PT009 UP007
import typing as ta
import unittest

from .. import reflect as rfl


class TestReflect(unittest.TestCase):
    def test_is_optional_alias(self):
        assert rfl.is_union_alias(ta.Union[int, str])
        assert rfl.is_union_alias(ta.Optional[int])
        assert not rfl.is_union_alias(int)

    def test_is_new_type(self):
        assert not rfl.is_new_type(int)
        assert rfl.is_new_type(ta.NewType('Foo', int))
