import unittest

from .. import system as sp
from ..types import InterpSpecifier


class TestBaseProviders(unittest.TestCase):
    def test_system(self):
        v = sp.SystemInterpProvider().installed_versions(InterpSpecifier.parse('3.12'))
        print(sp.SystemInterpProvider().get_version(v[0]))

    def test_system_exes(self):
        print(sp.SystemInterpProvider().exes())
