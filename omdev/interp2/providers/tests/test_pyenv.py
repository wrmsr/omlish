import sys
import unittest

from ....amalg.std.tests.helpers import SubprocessPatchingTest
from .. import pyenv as pe


class TestPyenv(SubprocessPatchingTest, unittest.TestCase):
    @unittest.skipUnless(sys.platform == 'darwin', 'requires darwin')
    def test_darwin(self):
        print(pe.DarwinPyenvInstallOpts().opts())

    @unittest.skipUnless(sys.platform == 'linux', 'requires linux')
    def test_linux(self):
        print(pe.LinuxPyenvInstallOpts().opts())

    def test_pyenv(self):
        p = pe.PyenvInterpProvider()
        print(p.guess_installed())
        print(p.query_installed())
