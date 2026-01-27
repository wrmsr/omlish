# @omlish-lite
import queue

from omlish.testing.unittest.asyncs import AsyncioIsolatedAsyncTestCase

from ..queues import AsyncioAsyncliteQueues


class TestAsyncioQueues(AsyncioIsolatedAsyncTestCase):
    async def test_basic_operations(self):
        api = AsyncioAsyncliteQueues()
        q = api.make_queue(maxsize=2)

        self.assertTrue(q.empty())
        self.assertFalse(q.full())
        self.assertEqual(q.qsize(), 0)

        await q.put('first')
        self.assertFalse(q.empty())
        self.assertFalse(q.full())
        self.assertEqual(q.qsize(), 1)

        await q.put('second')
        self.assertFalse(q.empty())
        self.assertTrue(q.full())
        self.assertEqual(q.qsize(), 2)

    async def test_put_get(self):
        api = AsyncioAsyncliteQueues()
        q = api.make_queue()

        await q.put('hello')
        await q.put('world')

        item1 = await q.get()
        self.assertEqual(item1, 'hello')

        item2 = await q.get()
        self.assertEqual(item2, 'world')

        self.assertTrue(q.empty())

    async def test_put_get_nowait(self):
        api = AsyncioAsyncliteQueues()
        q = api.make_queue(maxsize=2)

        q.put_nowait('first')
        q.put_nowait('second')

        self.assertEqual(q.qsize(), 2)
        self.assertTrue(q.full())

        item1 = q.get_nowait()
        self.assertEqual(item1, 'first')

        item2 = q.get_nowait()
        self.assertEqual(item2, 'second')

        self.assertTrue(q.empty())

    async def test_get_nowait_empty(self):
        api = AsyncioAsyncliteQueues()
        q = api.make_queue()

        with self.assertRaises(queue.Empty):
            q.get_nowait()

    async def test_put_nowait_full(self):
        api = AsyncioAsyncliteQueues()
        q = api.make_queue(maxsize=1)

        q.put_nowait('item')

        with self.assertRaises(queue.Full):
            q.put_nowait('another')

    async def test_put_timeout(self):
        api = AsyncioAsyncliteQueues()
        q = api.make_queue(maxsize=1)

        await q.put('first')
        self.assertTrue(q.full())

        with self.assertRaises(TimeoutError):
            await q.put('second', timeout=0.1)

    async def test_get_timeout(self):
        api = AsyncioAsyncliteQueues()
        q = api.make_queue()

        self.assertTrue(q.empty())

        with self.assertRaises(TimeoutError):
            await q.get(timeout=0.1)

    async def test_unbounded_queue(self):
        api = AsyncioAsyncliteQueues()
        q = api.make_queue()

        for i in range(100):
            await q.put(i)

        self.assertEqual(q.qsize(), 100)
        self.assertFalse(q.full())

        for i in range(100):
            item = await q.get()
            self.assertEqual(item, i)

        self.assertTrue(q.empty())
