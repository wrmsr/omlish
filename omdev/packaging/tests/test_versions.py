# ruff: noqa: PT009
import sys
import unittest

from ..versions import Version


class TestVersions(unittest.TestCase):
    def test_versions(self):
        for s in [
            sys.version.split()[0],
            '3.13.0rc1',
        ]:
            print(s)
            v = Version(s)
            print(v)
