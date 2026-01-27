import asyncio
import unittest

from ..events import SyncAsyncliteEvents


class TestSyncEvents(unittest.TestCase):
    def test_initial_state(self):
        async def _test():
            api = SyncAsyncliteEvents()
            event = api.make_event()

            self.assertFalse(event.is_set())

        asyncio.run(_test())

    def test_set_and_is_set(self):
        async def _test():
            api = SyncAsyncliteEvents()
            event = api.make_event()

            self.assertFalse(event.is_set())

            event.set()
            self.assertTrue(event.is_set())

        asyncio.run(_test())

    def test_wait_when_set(self):
        async def _test():
            api = SyncAsyncliteEvents()
            event = api.make_event()

            event.set()
            await event.wait()

            self.assertTrue(event.is_set())

        asyncio.run(_test())

    def test_set_is_idempotent(self):
        async def _test():
            api = SyncAsyncliteEvents()
            event = api.make_event()

            event.set()
            self.assertTrue(event.is_set())

            event.set()
            self.assertTrue(event.is_set())

            await event.wait()
            self.assertTrue(event.is_set())

        asyncio.run(_test())
