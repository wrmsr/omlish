# ruff: noqa: PT009
import unittest

from ...tests.test_subprocesses import SubprocessPatchingTest
from ..specifiers import Specifier


class TestSpecifiers(SubprocessPatchingTest, unittest.TestCase):
    def test_specifiers(self):
        for v, s in [
                ('2.0', '==2'),
                ('2.0', '==2.0'),
                ('2.0', '==2.0.0'),
        ]:
            self.assertTrue(Specifier(s).contains(v))
