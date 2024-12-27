# ruff: noqa: PT009
# @omlish-lite
import unittest

from ..flattening import ConfigFlattening


class TestFlattening(unittest.TestCase):
    def test_flattening(self):
        m = {
            'a': 1,
            'b': {
                'c': 2,
            },
            'd': [
                'e',
                {
                    'f': 3,
                },
            ],
            'g': [
                [
                    'a',
                    'b',
                ],
                [
                    'c',
                    'd',
                ],
            ],
        }
        for f in [
            ConfigFlattening(),
            ConfigFlattening(index_open='[', index_close=']'),
            ConfigFlattening(index_open='((', index_close='))'),
        ]:
            fl = f.flatten(m)
            ufl = f.unflatten(fl)
            self.assertEqual(ufl, m)
