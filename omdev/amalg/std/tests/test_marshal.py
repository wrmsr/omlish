# ruff: noqa: PT009
import unittest

from .. import marshal as msh


class TestMarshal(unittest.TestCase):
    def test_marshal(self):
        self.assertEqual(msh.marshal_obj(5), 5)

    def test_unmarshal(self):
        self.assertEqual(msh.unmarshal_obj(5, int), 5)
