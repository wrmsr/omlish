import unittest

from .. import standalone as sd


class TestStandalone(unittest.TestCase):
    def test_standalone(self):
        print(sd.list_pythons())
