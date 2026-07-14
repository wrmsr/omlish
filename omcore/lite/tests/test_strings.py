# ruff: noqa: PT009
import unittest

from ..strings import format_num_bytes


class TestStrings(unittest.TestCase):
    def test_format_num_bytes(self):
        self.assertEqual(format_num_bytes(4096), '4kB')
        self.assertEqual(format_num_bytes(4321500), '4.12MB')
        self.assertEqual(format_num_bytes(4294967296), '4GB')
