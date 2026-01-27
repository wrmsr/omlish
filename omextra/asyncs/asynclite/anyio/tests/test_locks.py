import anyio

from omlish.testing.unittest.asyncs import AnyioIsolatedAsyncTestCase

from ..locks import AnyioAsyncliteLocks


def run_anyio_test(test_fn):
    """Helper to run an async test function with anyio."""

    anyio.run(test_fn)


class TestAnyioLocks(AnyioIsolatedAsyncTestCase):
    async def test_basic_lock_unlock(self):
        api = AnyioAsyncliteLocks()
        lock = api.make_lock()

        self.assertFalse(lock.locked())

        await lock.acquire()
        self.assertTrue(lock.locked())

        lock.release()
        self.assertFalse(lock.locked())

    async def test_lock_prevents_concurrent_access(self):
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

    async def test_context_manager(self):
        api = AnyioAsyncliteLocks()
        lock = api.make_lock()

        self.assertFalse(lock.locked())

        async with lock:
            self.assertTrue(lock.locked())

        self.assertFalse(lock.locked())

    async def test_multiple_acquire_release(self):
        api = AnyioAsyncliteLocks()
        lock = api.make_lock()

        for _ in range(3):
            self.assertFalse(lock.locked())
            await lock.acquire()
            self.assertTrue(lock.locked())
            lock.release()

        self.assertFalse(lock.locked())

    async def test_nested_context_manager(self):
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

    async def test_acquire_nowait_succeeds(self):
        api = AnyioAsyncliteLocks()
        lock = api.make_lock()

        self.assertFalse(lock.locked())

        result = lock.acquire_nowait()
        self.assertTrue(result)
        self.assertTrue(lock.locked())

        lock.release()
        self.assertFalse(lock.locked())

    async def test_acquire_nowait_fails_when_locked(self):
        api = AnyioAsyncliteLocks()
        lock = api.make_lock()

        # Have another task acquire the lock
        lock_acquired = anyio.Event()
        lock_release = anyio.Event()

        async def holder():
            await lock.acquire()
            lock_acquired.set()
            await lock_release.wait()
            lock.release()

        async with anyio.create_task_group() as tg:
            tg.start_soon(holder)
            await lock_acquired.wait()

            # Now try acquire_nowait from this task - should fail
            self.assertTrue(lock.locked())
            result = lock.acquire_nowait()
            self.assertFalse(result)
            self.assertTrue(lock.locked())

            # Release and verify
            lock_release.set()

        self.assertFalse(lock.locked())
