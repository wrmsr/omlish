# @omlish-lite
import unittest

from ..check import check


class TestAsyncChecks(unittest.IsolatedAsyncioTestCase):
    async def test_async_single_gens(self):
        async def f0():
            return
            yield  # noqa

        with self.assertRaises(ValueError):
            await check.async_single(f0())
        self.assertEqual(await check.async_opt_single(f0()), None)

        async def f1():
            yield 1

        self.assertEqual(await check.async_single(f1()), 1)
        self.assertEqual(await check.async_opt_single(f1()), 1)

        async def f2():
            yield 1
            yield 2

        with self.assertRaises(ValueError):
            await check.async_single(f2())
        with self.assertRaises(ValueError):
            await check.async_opt_single(f2())

    class _FooAsyncIter:
        def __init__(self, obj):
            self._it = iter(obj)

        def __aiter__(self):
            return self

        async def __anext__(self):
            try:
                return next(self._it)
            except StopIteration:
                raise StopAsyncIteration from None

    async def test_async_single_lists(self):
        def f0():
            return self._FooAsyncIter([])

        with self.assertRaises(ValueError):
            await check.async_single(f0())
        self.assertEqual(await check.async_opt_single(f0()), None)

        def f1():
            return self._FooAsyncIter([1])

        self.assertEqual(await check.async_single(f1()), 1)
        self.assertEqual(await check.async_opt_single(f1()), 1)

        def f2():
            return self._FooAsyncIter([1, 2])

        with self.assertRaises(ValueError):
            await check.async_single(f2())
        with self.assertRaises(ValueError):
            await check.async_opt_single(f2())
