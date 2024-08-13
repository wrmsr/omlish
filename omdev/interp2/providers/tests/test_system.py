import unittest

from .. import system as sp
from ....amalg.std.versions.specifiers import SpecifierSet


class TestBaseProviders(unittest.TestCase):
    def test_system(self):
        v = sp.SystemInterpProvider().installed_versions(SpecifierSet('3'))
        print(sp.SystemInterpProvider().get_version(v[0]))

    def test_system_exes(self):
        print(sp.SystemInterpProvider().exes())
