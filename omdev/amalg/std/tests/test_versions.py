# ruff: noqa: PT009 PT027
import sys
import unittest

from ..versions import parse_version


class TestVersions(unittest.TestCase):
    def test_versions(self):
        for s in [
            sys.version.split()[0],
            '3.13.0rc1',
        ]:
            print(s)
            v = parse_version(s)
            print(v)
