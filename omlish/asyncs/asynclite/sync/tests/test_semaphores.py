# @omlish-lite
from .....testing.unittest.asyncs import SyncIsolatedAsyncTestCase
from ..semaphores import SyncAsyncliteSemaphores


class TestSyncSemaphores(SyncIsolatedAsyncTestCase):
    async def test_basic_acquire_release(self):
        api = SyncAsyncliteSemaphores()
        sem = api.make_semaphore(1)

        await sem.acquire()
        sem.release()

    async def test_multiple_acquire_release(self):
        api = SyncAsyncliteSemaphores()
        sem = api.make_semaphore(3)

        await sem.acquire()
        await sem.acquire()
        await sem.acquire()

        sem.release()
        sem.release()
        sem.release()

    async def test_context_manager(self):
        api = SyncAsyncliteSemaphores()
        sem = api.make_semaphore(1)

        async with sem:
            pass

    async def test_acquire_nowait_succeeds(self):
        api = SyncAsyncliteSemaphores()
        sem = api.make_semaphore(2)

        result1 = sem.acquire_nowait()
        self.assertTrue(result1)

        result2 = sem.acquire_nowait()
        self.assertTrue(result2)

        sem.release()
        sem.release()

    async def test_acquire_nowait_fails_when_exhausted(self):
        api = SyncAsyncliteSemaphores()
        sem = api.make_semaphore(1)

        await sem.acquire()

        result = sem.acquire_nowait()
        self.assertFalse(result)

        sem.release()

    async def test_semaphore_with_multiple_slots(self):
        api = SyncAsyncliteSemaphores()
        sem = api.make_semaphore(3)
        results = []

        async def worker(name: str):
            await sem.acquire()
            results.append(f'{name}_start')
            results.append(f'{name}_end')
            sem.release()

        await worker('w1')
        await worker('w2')
        await worker('w3')
        await worker('w4')

        # All 4 workers should complete
        self.assertEqual(len(results), 8)

    async def test_release_increments_counter(self):
        api = SyncAsyncliteSemaphores()
        sem = api.make_semaphore(1)

        await sem.acquire()
        sem.release()

        # Should be able to acquire again
        await sem.acquire()
        sem.release()
