# ruff: noqa: PT009 PT027
import dataclasses as dc
import unittest

from ..dataclasses import cache_dataclass_hash


@dc.dataclass()
class CountingHashThing:
    hash: int = 0
    num_times_hashed: int = 0

    def __hash__(self):
        self.num_times_hashed += 1
        return self.hash


class TestDataclasses(unittest.TestCase):
    def test_cache_hash(self):
        @dc.dataclass(frozen=True)
        class Foo:
            thing: CountingHashThing = dc.field(default_factory=CountingHashThing)

        f = Foo()
        h1 = hash(f)
        self.assertEqual(f.thing.num_times_hashed, 1)
        h2 = hash(f)
        self.assertEqual(f.thing.num_times_hashed, 2)
        self.assertEqual(h1, h2)

        cache_dataclass_hash()(Foo)

        f = Foo()
        h1 = hash(f)
        self.assertEqual(f.thing.num_times_hashed, 1)
        h2 = hash(f)
        self.assertEqual(f.thing.num_times_hashed, 1)
        self.assertEqual(h1, h2)
