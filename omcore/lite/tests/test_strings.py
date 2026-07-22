# ruff: noqa: PT009
import unittest

from ..strings import format_num_bytes
from ..strings import is_sunder
from ..strings import split_keep_delimiter


class TestStrings(unittest.TestCase):
    def test_format_num_bytes(self):
        self.assertEqual(format_num_bytes(4096), '4kB')
        self.assertEqual(format_num_bytes(4321500), '4.12MB')
        self.assertEqual(format_num_bytes(4294967296), '4GB')

    def test_is_sunder(self):
        self.assertTrue(is_sunder('_foo_'))
        self.assertFalse(is_sunder('__foo__'))
        self.assertFalse(is_sunder('_'))
        self.assertFalse(is_sunder('__'))
        self.assertFalse(is_sunder(''))

    def test_split_keep_delimiter(self):
        self.assertEqual(split_keep_delimiter('a\nb\nc', '\n'), ['a\n', 'b\n', 'c'])
        self.assertEqual(split_keep_delimiter('a\nb\n', '\n'), ['a\n', 'b\n'])
        self.assertEqual(split_keep_delimiter('abc', '\n'), ['abc'])
        self.assertEqual(split_keep_delimiter('', '\n'), [])
        self.assertEqual(split_keep_delimiter('abXYcdXY', 'XY'), ['abXY', 'cdXY'])
        self.assertEqual(split_keep_delimiter('abXYcd', 'XY'), ['abXY', 'cd'])
        self.assertEqual(split_keep_delimiter(b'a\r\nb', b'\r\n'), [b'a\r\n', b'b'])

        with self.assertRaises(ValueError):
            split_keep_delimiter('ab', '')
