import unittest

from .. import base as bp
from ....amalg.std.versions.specifiers import SpecifierSet


class TestBaseProviders(unittest.TestCase):
    def test_running(self):
        v = bp.RunningInterpProvider().installed_versions(SpecifierSet('3'))
        print(bp.RunningInterpProvider().get_version(v[0]))
