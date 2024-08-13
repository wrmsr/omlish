import unittest

from .. import system as sp


class TestBaseProviders(unittest.TestCase):
    def test_system(self):
        v = sp.SystemInterpProvider().installed_versions()
        print(sp.SystemInterpProvider().get_version(v[0]))

    def test_system_exes(self):
        print(sp.SystemInterpProvider().exes())
