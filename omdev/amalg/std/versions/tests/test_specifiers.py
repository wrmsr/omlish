# ruff: noqa: PT009 PT027
import unittest

from ..specifiers import Specifier


class TestSpecifiers(unittest.TestCase):
    def test_specifiers(self):
        for v, s in [
                ('2.0', '==2'),
                ('2.0', '==2.0'),
                ('2.0', '==2.0.0'),
        ]:
            self.assertTrue(Specifier(s).contains(v))
