import unittest
import sys

from .. import pyenv as pe


class TestPyenv(unittest.TestCase):
    def test_pyenv(self):
        p = pe.PyenvInterpProvider()
        print(p)

    @unittest.skipUnless(sys.platform == 'darwin', 'requires darwin')
    def test_mac(self):
        pass

    @unittest.skipUnless(sys.platform == 'linux', 'requires linux')
    def test_linux(self):
        pass

