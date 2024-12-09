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
            assert f() == 'f'
            assert c == 1

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
            assert c0.f() == 'c0'
            assert c == 1

        c1 = C('c1')
        for _ in range(2):
            assert c1.f() == 'c1'
            assert c == 2

        assert c0.f() == 'c0'
        assert c1.f() == 'c1'
        assert c == 2


class TestCachedAsync(unittest.IsolatedAsyncioTestCase):
    async def test_cached_nullary_async(self):
        c = 0

        @cached.async_cached_nullary
        async def f():
            nonlocal c
            c += 1
            return 'f'

        for _ in range(2):
            assert await f() == 'f'
            assert c == 1
