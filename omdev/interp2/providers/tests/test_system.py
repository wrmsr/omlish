import unittest

from .. import system as sp


class TestBaseProviders(unittest.TestCase):
    def test_system(self):
        v = sp.SystemInterpProvider().installed_versions()
        print(sp.SystemInterpProvider().get_version(v[0]))
