import unittest

from ..toposort import toposort


class TestToposort(unittest.TestCase):
    def test_toposort(self):
        toposort({
            0: frozenset(),
        })
