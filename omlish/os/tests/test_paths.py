# ruff: noqa: PT009
# @omlish-lite
import unittest

from ..paths import is_path_in_dir


class TestPaths(unittest.TestCase):
    def test_is_path_in_dir(self):
        self.assertTrue(is_path_in_dir('/a/b/', '/a/b/c'))
        self.assertFalse(is_path_in_dir('/a/b/', '/a/bb/c'))
