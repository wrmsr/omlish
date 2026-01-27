import unittest

import anyio

from ..locks import AnyioAsyncliteLocks


def run_anyio_test(test_fn):
    """Helper to run an async test function with anyio."""

    anyio.run(test_fn)


class TestAnyioLocks(unittest.TestCase):
    def test_basic_lock_unlock(self):
        async def _test():
            api = AnyioAsyncliteLocks()
            lock = api.make_lock()

            self.assertFalse(lock.locked())

            await lock.acquire()
            self.assertTrue(lock.locked())

            lock.release()
            self.assertFalse(lock.locked())

        run_anyio_test(_test)

    def test_lock_prevents_concurrent_access(self):
        async def _test():
            api = AnyioAsyncliteLocks()
            lock = api.make_lock()
            results = []

            async def worker(name: str):
                await lock.acquire()
                results.append(f'{name}_start')
                results.append(f'{name}_end')
                lock.release()

            await lock.acquire()
            self.assertTrue(lock.locked())
            lock.release()

            await worker('first')
            await worker('second')

            self.assertEqual(results, ['first_start', 'first_end', 'second_start', 'second_end'])

        run_anyio_test(_test)

    def test_context_manager(self):
        async def _test():
            api = AnyioAsyncliteLocks()
            lock = api.make_lock()

            self.assertFalse(lock.locked())

            async with lock:
                self.assertTrue(lock.locked())

            self.assertFalse(lock.locked())

        run_anyio_test(_test)


    def test_multiple_acquire_release(self):
        async def _test():
            api = AnyioAsyncliteLocks()
            lock = api.make_lock()

            for _ in range(3):
                self.assertFalse(lock.locked())
                await lock.acquire()
                self.assertTrue(lock.locked())
                lock.release()

            self.assertFalse(lock.locked())

        run_anyio_test(_test)

    def test_nested_context_manager(self):
        async def _test():
            api = AnyioAsyncliteLocks()
            lock1 = api.make_lock()
            lock2 = api.make_lock()

            async with lock1:
                self.assertTrue(lock1.locked())
                self.assertFalse(lock2.locked())

                async with lock2:
                    self.assertTrue(lock1.locked())
                    self.assertTrue(lock2.locked())

                self.assertTrue(lock1.locked())
                self.assertFalse(lock2.locked())

            self.assertFalse(lock1.locked())
            self.assertFalse(lock2.locked())

        run_anyio_test(_test)
