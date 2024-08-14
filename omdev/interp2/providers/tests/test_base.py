import unittest

from ....amalg.std.versions.specifiers import SpecifierSet
from .. import base as bp


class TestBaseProviders(unittest.TestCase):
    def test_running(self):
        v = bp.RunningInterpProvider().installed_versions(SpecifierSet('~=3.12'))
        print(bp.RunningInterpProvider().get_version(v[0]))
