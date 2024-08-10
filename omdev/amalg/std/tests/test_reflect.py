# ruff: noqa: PT009 UP006
import typing as ta
import unittest

from .. import reflect as rfl


class TestMarshal(unittest.TestCase):
    def test_is_list_typing(self):
        assert rfl.is_list_alias(ta.List)
        assert rfl.is_list_alias(ta.List[int])
        assert not rfl.is_list_alias(ta.Dict[int, int])
        assert not rfl.is_dict_alias(ta.List[int])

    def test_is_dict_typing(self):
        assert rfl.is_dict_alias(ta.Dict)
        assert rfl.is_dict_alias(ta.Dict[int, int])
        assert not rfl.is_dict_alias(ta.List[int])
        assert not rfl.is_list_alias(ta.Dict[int, int])
