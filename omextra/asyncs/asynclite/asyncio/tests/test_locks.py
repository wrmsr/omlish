from omlish.testing.unittest.asyncs import AsyncioIsolatedAsyncTestCase

from ..locks import AsyncioAsyncliteLocks


class TestAsyncioLocks(AsyncioIsolatedAsyncTestCase):
    async def test_basic_lock_unlock(self):
        api = AsyncioAsyncliteLocks()
        lock = api.make_lock()

        self.assertFalse(lock.locked())

        await lock.acquire()
        self.assertTrue(lock.locked())

        lock.release()
        self.assertFalse(lock.locked())

    async def test_lock_prevents_concurrent_access(self):
        api = AsyncioAsyncliteLocks()
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

    async def test_context_manager(self):
        api = AsyncioAsyncliteLocks()
        lock = api.make_lock()

        self.assertFalse(lock.locked())

        async with lock:
            self.assertTrue(lock.locked())

        self.assertFalse(lock.locked())

    async def test_acquire_timeout(self):
        api = AsyncioAsyncliteLocks()
        lock = api.make_lock()

        await lock.acquire()
        self.assertTrue(lock.locked())

        with self.assertRaises(TimeoutError):
            await lock.acquire(timeout=0.1)

        lock.release()
        self.assertFalse(lock.locked())

    async def test_multiple_acquire_release(self):
        api = AsyncioAsyncliteLocks()
        lock = api.make_lock()

        for _ in range(3):
            self.assertFalse(lock.locked())
            await lock.acquire()
            self.assertTrue(lock.locked())
            lock.release()

        self.assertFalse(lock.locked())

    async def test_nested_context_manager(self):
        api = AsyncioAsyncliteLocks()
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

    async def test_acquire_nowait_succeeds(self):
        api = AsyncioAsyncliteLocks()
        lock = api.make_lock()

        self.assertFalse(lock.locked())

        result = lock.acquire_nowait()
        self.assertTrue(result)
        self.assertTrue(lock.locked())

        lock.release()
        self.assertFalse(lock.locked())

    async def test_acquire_nowait_fails_when_locked(self):
        import asyncio

        api = AsyncioAsyncliteLocks()
        lock = api.make_lock()

        # Have another task acquire the lock
        lock_acquired = asyncio.Event()
        lock_release = asyncio.Event()

        async def holder():
            await lock.acquire()
            lock_acquired.set()
            await lock_release.wait()
            lock.release()

        task = asyncio.create_task(holder())
        await lock_acquired.wait()

        # Now try acquire_nowait from this task - should fail
        self.assertTrue(lock.locked())
        result = lock.acquire_nowait()
        self.assertFalse(result)
        self.assertTrue(lock.locked())

        # Release and verify
        lock_release.set()
        await task
        self.assertFalse(lock.locked())
