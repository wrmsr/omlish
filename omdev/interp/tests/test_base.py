import unittest

from .. import providers as bp
from ..types import InterpSpecifier


class TestBaseProviders(unittest.TestCase):
    def test_running(self):
        v = bp.RunningInterpProvider().get_installed_versions(InterpSpecifier.parse('3.12'))
        print(bp.RunningInterpProvider().get_installed_version(v[0]))
