import unittest

from ..strings import format_num_bytes


class TestStrings(unittest.TestCase):
    def test_format_num_bytes(self):
        assert format_num_bytes(4096) == '4kB'
        assert format_num_bytes(4321500) == '4.12MB'
        assert format_num_bytes(4294967296) == '4GB'
