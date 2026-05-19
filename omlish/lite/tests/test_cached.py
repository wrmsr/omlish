# ruff: noqa: PT009 UP006
import dataclasses as dc
import typing as ta
import unittest

from .. import cached


class TestCached(unittest.TestCase):
    def test_cached_nullary_function(self):
        c = 0

        @cached.cached_nullary
        def f():
            nonlocal c
            c += 1
            return 'f'

        for _ in range(2):
            self.assertEqual(f(), 'f')
            self.assertEqual(c, 1)

    def test_cached_nullary_method(self):
        c = 0

        class C:
            def __init__(self, f):
                super().__init__()
                self._f = f

            @cached.cached_nullary
            def f(self):
                nonlocal c
                c += 1
                return self._f

        c0 = C('c0')
        for _ in range(2):
            self.assertEqual(c0.f(), 'c0')
            self.assertEqual(c, 1)

        c1 = C('c1')
        for _ in range(2):
            self.assertEqual(c1.f(), 'c1')
            self.assertEqual(c, 2)

        self.assertEqual(c0.f(), 'c0')
        self.assertEqual(c1.f(), 'c1')
        self.assertEqual(c, 2)

    def test_cached_property_frozen_dc(self):
        @dc.dataclass(frozen=True)
        class Foo:
            x: int = 100
            c: ta.List[int] = dc.field(default_factory=lambda: [0])

            @cached.cached_property
            def y(self):
                self.c[0] += 1
                return self.x + 1

        foo = Foo()
        assert foo.x == 100
        assert foo.c == [0]
        for _ in range(2):
            assert foo.y == 101
            assert foo.c == [1]


class TestCachedAsync(unittest.IsolatedAsyncioTestCase):
    async def test_cached_nullary_async(self):
        c = 0

        @cached.async_cached_nullary
        async def f():
            nonlocal c
            c += 1
            return 'f'

        for _ in range(2):
            self.assertEqual(await f(), 'f')
            self.assertEqual(c, 1)
