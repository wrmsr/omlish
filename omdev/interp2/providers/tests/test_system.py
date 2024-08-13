import unittest

from .. import system as sp


class TestBaseProviders(unittest.TestCase):
    def test_system(self):
        from omlish import logs
        logs.configure_standard_logging('DEBUG')
        v = sp.SystemInterpProvider().installed_versions()
        print(sp.SystemInterpProvider().get_version(v[0]))
