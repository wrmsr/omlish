# ruff: noqa: PT009
import unittest

from ..specifiers import Specifier
from ..specifiers import SpecifierSet


class TestSpecifiers(unittest.TestCase):
    def test_specifiers(self):
        for v, s in [
                ('2.0', '==2'),
                ('2.0', '==2.0'),
                ('2.0', '==2.0.0'),
        ]:
            self.assertTrue(Specifier(s).contains(v))

    def test_create_from_specifiers(self):
        spec_strs = [
            '>=1.0',
            '!=1.1',
            '!=1.2',
            '<2.0',
        ]
        specs = [Specifier(s) for s in spec_strs]
        spec = SpecifierSet(iter(specs))
        assert set(spec) == set(specs)
