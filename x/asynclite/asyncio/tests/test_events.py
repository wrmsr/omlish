import asyncio
import unittest

from ..events import AsyncioAsyncliteEvents


class TestAsyncioEvents(unittest.IsolatedAsyncioTestCase):
    async def test_initial_state(self):
        api = AsyncioAsyncliteEvents()
        event = api.make_event()

        self.assertFalse(event.is_set())

    async def test_set_and_is_set(self):
        api = AsyncioAsyncliteEvents()
        event = api.make_event()

        self.assertFalse(event.is_set())

        event.set()
        self.assertTrue(event.is_set())

    async def test_wait_when_set(self):
        api = AsyncioAsyncliteEvents()
        event = api.make_event()

        event.set()
        await event.wait()

        self.assertTrue(event.is_set())

    async def test_wait_blocks_until_set(self):
        api = AsyncioAsyncliteEvents()
        event = api.make_event()
        result = []

        async def waiter():
            result.append('waiting')
            await event.wait()
            result.append('done')

        task = asyncio.create_task(waiter())
        await asyncio.sleep(0.01)

        self.assertEqual(result, ['waiting'])
        self.assertFalse(event.is_set())

        event.set()
        await task

        self.assertEqual(result, ['waiting', 'done'])
        self.assertTrue(event.is_set())

    async def test_wait_timeout(self):
        api = AsyncioAsyncliteEvents()
        event = api.make_event()

        self.assertFalse(event.is_set())

        with self.assertRaises(TimeoutError):
            await event.wait(timeout=0.1)

        self.assertFalse(event.is_set())

    async def test_multiple_waiters(self):
        api = AsyncioAsyncliteEvents()
        event = api.make_event()
        results = []

        async def waiter(name: str):
            await event.wait()
            results.append(name)

        tasks = [
            asyncio.create_task(waiter('first')),
            asyncio.create_task(waiter('second')),
            asyncio.create_task(waiter('third')),
        ]

        await asyncio.sleep(0.01)
        self.assertEqual(results, [])

        event.set()
        await asyncio.gather(*tasks)

        self.assertEqual(sorted(results), ['first', 'second', 'third'])

    async def test_set_is_idempotent(self):
        api = AsyncioAsyncliteEvents()
        event = api.make_event()

        event.set()
        self.assertTrue(event.is_set())

        event.set()
        self.assertTrue(event.is_set())

        await event.wait()
        self.assertTrue(event.is_set())
