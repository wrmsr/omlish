import unittest

from .. import pyenv as pe


class TestPyenv(unittest.TestCase):
    def test_pyenv(self):
        p = pe.PyenvInterpProvider()
        print(p.pyenv_root())
