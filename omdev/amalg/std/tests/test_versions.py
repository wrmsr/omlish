# ruff: noqa: PT009 PT027
import unittest

from ..versions import parse_version


class TestVersions(unittest.TestCase):
    def test_versions(self):
        v = parse_version('3.13.0rc1')
        print(v)
