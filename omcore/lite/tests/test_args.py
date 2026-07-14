# ruff: noqa: PT009
import unittest

from ..args import Args


class ArgsTest(unittest.TestCase):
    def test_args(self):
        def f(x, y, z):
            return x + y * z

        self.assertEqual(Args(1, 2, 3)(f), 7)
