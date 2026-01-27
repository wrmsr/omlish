import asyncio

from omlish.testing.unittest.asyncs import AsyncioIsolatedAsyncTestCase

from ..semaphores import AsyncioAsyncliteSemaphores


class TestAsyncioSemaphores(AsyncioIsolatedAsyncTestCase):
    async def test_basic_acquire_release(self):
        api = AsyncioAsyncliteSemaphores()
        sem = api.make_semaphore(1)

        await sem.acquire()
        sem.release()

    async def test_multiple_acquire_release(self):
        api = AsyncioAsyncliteSemaphores()
        sem = api.make_semaphore(3)

        await sem.acquire()
        await sem.acquire()
        await sem.acquire()

        sem.release()
        sem.release()
        sem.release()

    async def test_acquire_blocks_when_exhausted(self):
        api = AsyncioAsyncliteSemaphores()
        sem = api.make_semaphore(1)
        result = []

        async def worker():
            await sem.acquire()
            result.append('acquired')
            await asyncio.sleep(0.05)
            sem.release()
            result.append('released')

        # First worker acquires immediately
        task1 = asyncio.create_task(worker())
        await asyncio.sleep(0.01)

        # Second worker blocks
        task2 = asyncio.create_task(worker())
        await asyncio.sleep(0.01)

        self.assertEqual(result, ['acquired'])

        await task1
        await task2

        self.assertEqual(result, ['acquired', 'released', 'acquired', 'released'])

    async def test_context_manager(self):
        api = AsyncioAsyncliteSemaphores()
        sem = api.make_semaphore(1)

        async with sem:
            pass

    async def test_acquire_nowait_succeeds(self):
        api = AsyncioAsyncliteSemaphores()
        sem = api.make_semaphore(2)

        result1 = sem.acquire_nowait()
        self.assertTrue(result1)

        result2 = sem.acquire_nowait()
        self.assertTrue(result2)

        sem.release()
        sem.release()

    async def test_acquire_nowait_fails_when_exhausted(self):
        api = AsyncioAsyncliteSemaphores()
        sem = api.make_semaphore(1)

        await sem.acquire()

        result = sem.acquire_nowait()
        self.assertFalse(result)

        sem.release()

    async def test_acquire_timeout(self):
        api = AsyncioAsyncliteSemaphores()
        sem = api.make_semaphore(1)

        await sem.acquire()

        with self.assertRaises(TimeoutError):
            await sem.acquire(timeout=0.1)

        sem.release()

    async def test_semaphore_with_multiple_slots(self):
        api = AsyncioAsyncliteSemaphores()
        sem = api.make_semaphore(3)
        results = []

        async def worker(name: str):
            await sem.acquire()
            results.append(f'{name}_start')
            await asyncio.sleep(0.01)
            results.append(f'{name}_end')
            sem.release()

        tasks = [
            asyncio.create_task(worker('w1')),
            asyncio.create_task(worker('w2')),
            asyncio.create_task(worker('w3')),
            asyncio.create_task(worker('w4')),
        ]

        await asyncio.gather(*tasks)

        # All 4 workers should complete
        self.assertEqual(len(results), 8)
        self.assertEqual(results.count('w1_start'), 1)
        self.assertEqual(results.count('w1_end'), 1)

    async def test_release_increments_counter(self):
        api = AsyncioAsyncliteSemaphores()
        sem = api.make_semaphore(1)

        await sem.acquire()
        sem.release()

        # Should be able to acquire again
        await sem.acquire()
        sem.release()
