import unittest

from .. import base as bp
from ..types import InterpSpecifier


class TestBaseProviders(unittest.TestCase):
    def test_running(self):
        v = bp.RunningInterpProvider().installed_versions(InterpSpecifier.parse('3.12'))
        print(bp.RunningInterpProvider().get_version(v[0]))
