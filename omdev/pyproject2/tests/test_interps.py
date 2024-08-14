import unittest

from ..interps import VenvInterps


class TestInterps(unittest.TestCase):
    def test_venv_interps(self):
        print(VenvInterps().versions_file_pythons())
