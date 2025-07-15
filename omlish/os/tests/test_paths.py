# ruff: noqa: PT009 PT027
# @omlish-lite
import unittest

from ..paths import is_path_in_dir
from ..paths import path_dirname


class TestPaths(unittest.TestCase):
    def test_is_path_in_dir(self):
        self.assertTrue(is_path_in_dir('/a/b/', '/a/b/c'))
        self.assertFalse(is_path_in_dir('/a/b/', '/a/bb/c'))

    def test_path_dirname(self):
        self.assertEqual(path_dirname('/a/b/c/d'), '/a/b/c')
        self.assertEqual(path_dirname('/a/b/c/d', 2), '/a/b')
        self.assertRaises(ValueError, path_dirname, '/a/b/c/d', 5)
