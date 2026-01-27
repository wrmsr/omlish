import threading

from omlish.lite.asyncs import sync_await
from omlish.testing.unittest.asyncs import SyncIsolatedAsyncTestCase

from ..locks import SyncAsyncliteLocks


class TestSyncLocks(SyncIsolatedAsyncTestCase):
    async def test_basic_lock_unlock(self):
        api = SyncAsyncliteLocks()
        lock = api.make_lock()

        self.assertFalse(lock.locked())

        await lock.acquire()
        self.assertTrue(lock.locked())

        lock.release()
        self.assertFalse(lock.locked())

    async def test_lock_prevents_concurrent_access(self):
        api = SyncAsyncliteLocks()
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
        api = SyncAsyncliteLocks()
        lock = api.make_lock()

        self.assertFalse(lock.locked())

        async with lock:
            self.assertTrue(lock.locked())

        self.assertFalse(lock.locked())

    async def test_multiple_acquire_release(self):
        api = SyncAsyncliteLocks()
        lock = api.make_lock()

        for _ in range(3):
            self.assertFalse(lock.locked())
            await lock.acquire()
            self.assertTrue(lock.locked())
            lock.release()

        self.assertFalse(lock.locked())

    async def test_nested_context_manager(self):
        api = SyncAsyncliteLocks()
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

    def test_acquire_nowait_succeeds(self):
        api = SyncAsyncliteLocks()
        lock = api.make_lock()

        self.assertFalse(lock.locked())

        result = lock.acquire_nowait()
        self.assertTrue(result)
        self.assertTrue(lock.locked())

        lock.release()
        self.assertFalse(lock.locked())

    def test_acquire_nowait_fails_when_locked(self):
        api = SyncAsyncliteLocks()
        lock = api.make_lock()

        # Have another thread acquire the lock
        lock_acquired = threading.Event()
        lock_release = threading.Event()

        def holder():
            sync_await(lock.acquire())
            lock_acquired.set()
            lock_release.wait()
            lock.release()

        thread = threading.Thread(target=holder)
        thread.start()
        lock_acquired.wait()

        # Now try acquire_nowait from this thread - should fail
        self.assertTrue(lock.locked())
        result = lock.acquire_nowait()
        self.assertFalse(result)
        self.assertTrue(lock.locked())

        # Release and verify
        lock_release.set()
        thread.join()
        self.assertFalse(lock.locked())
