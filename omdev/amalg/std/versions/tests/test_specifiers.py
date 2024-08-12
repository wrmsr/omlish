# ruff: noqa: PT009 PT027
import unittest

from ..specifiers import Specifier


class TestSpecifiers(unittest.TestCase):
    def test_specifiers(self):
        self.assertTrue(Specifier('2.*').contains('2b1.dev1'))
