import unittest

import anyio

from ..semaphores import AnyioAsyncliteSemaphores


def run_anyio_test(test_fn):
    """Helper to run an async test function with anyio."""

    anyio.run(test_fn)


class TestAnyioSemaphores(unittest.TestCase):
    def test_basic_acquire_release(self):
        async def _test():
            api = AnyioAsyncliteSemaphores()
            sem = api.make_semaphore(1)

            await sem.acquire()
            sem.release()

        run_anyio_test(_test)

    def test_multiple_acquire_release(self):
        async def _test():
            api = AnyioAsyncliteSemaphores()
            sem = api.make_semaphore(3)

            await sem.acquire()
            await sem.acquire()
            await sem.acquire()

            sem.release()
            sem.release()
            sem.release()

        run_anyio_test(_test)

    def test_acquire_blocks_when_exhausted(self):
        async def _test():
            api = AnyioAsyncliteSemaphores()
            sem = api.make_semaphore(1)
            result = []

            async def worker():
                await sem.acquire()
                result.append('acquired')
                await anyio.sleep(0.05)
                sem.release()
                result.append('released')

            async with anyio.create_task_group() as tg:
                # First worker acquires immediately
                tg.start_soon(worker)
                await anyio.sleep(0.01)

                self.assertEqual(result, ['acquired'])

                # Second worker blocks
                tg.start_soon(worker)
                await anyio.sleep(0.01)

                self.assertEqual(result, ['acquired'])

            self.assertEqual(result, ['acquired', 'released', 'acquired', 'released'])

        run_anyio_test(_test)

    def test_context_manager(self):
        async def _test():
            api = AnyioAsyncliteSemaphores()
            sem = api.make_semaphore(1)

            async with sem:
                pass

        run_anyio_test(_test)

    def test_acquire_nowait_succeeds(self):
        async def _test():
            api = AnyioAsyncliteSemaphores()
            sem = api.make_semaphore(2)

            result1 = sem.acquire_nowait()
            self.assertTrue(result1)

            result2 = sem.acquire_nowait()
            self.assertTrue(result2)

            sem.release()
            sem.release()

        run_anyio_test(_test)

    def test_acquire_nowait_fails_when_exhausted(self):
        async def _test():
            api = AnyioAsyncliteSemaphores()
            sem = api.make_semaphore(1)

            await sem.acquire()

            result = sem.acquire_nowait()
            self.assertFalse(result)

            sem.release()

        run_anyio_test(_test)

    def test_acquire_timeout(self):
        async def _test():
            api = AnyioAsyncliteSemaphores()
            sem = api.make_semaphore(1)

            await sem.acquire()

            with self.assertRaises(TimeoutError):
                await sem.acquire(timeout=0.1)

            sem.release()

        run_anyio_test(_test)

    def test_semaphore_with_multiple_slots(self):
        async def _test():
            api = AnyioAsyncliteSemaphores()
            sem = api.make_semaphore(3)
            results = []

            async def worker(name: str):
                await sem.acquire()
                results.append(f'{name}_start')
                await anyio.sleep(0.01)
                results.append(f'{name}_end')
                sem.release()

            async with anyio.create_task_group() as tg:
                tg.start_soon(worker, 'w1')
                tg.start_soon(worker, 'w2')
                tg.start_soon(worker, 'w3')
                tg.start_soon(worker, 'w4')

            # All 4 workers should complete
            self.assertEqual(len(results), 8)
            self.assertEqual(results.count('w1_start'), 1)
            self.assertEqual(results.count('w1_end'), 1)

        run_anyio_test(_test)

    def test_release_increments_counter(self):
        async def _test():
            api = AnyioAsyncliteSemaphores()
            sem = api.make_semaphore(1)

            await sem.acquire()
            sem.release()

            # Should be able to acquire again
            await sem.acquire()
            sem.release()

        run_anyio_test(_test)
