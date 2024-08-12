import sys
import unittest

from .. import pyenv as pe


class TestPyenv(unittest.TestCase):
    @unittest.skipUnless(sys.platform == 'darwin', 'requires darwin')
    def test_darwin(self):
        print(pe.DarwinPyenvInstallOpts().install_opts())

    @unittest.skipUnless(sys.platform == 'linux', 'requires linux')
    def test_linux(self):
        print(pe.LinuxPyenvInstallOpts().install_opts())

    def test_pyenv(self):
        p = pe.PyenvInterpProvider()
        print(p.guess_installed())
        print(p.query_installed())
