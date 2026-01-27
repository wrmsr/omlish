# @omlish-lite
from .....testing.unittest.asyncs import SyncIsolatedAsyncTestCase
from ..events import SyncAsyncliteEvents


class TestSyncEvents(SyncIsolatedAsyncTestCase):
    async def test_initial_state(self):
        api = SyncAsyncliteEvents()
        event = api.make_event()

        self.assertFalse(event.is_set())

    async def test_set_and_is_set(self):
        api = SyncAsyncliteEvents()
        event = api.make_event()

        self.assertFalse(event.is_set())

        event.set()
        self.assertTrue(event.is_set())

    async def test_wait_when_set(self):
        api = SyncAsyncliteEvents()
        event = api.make_event()

        event.set()
        await event.wait()

        self.assertTrue(event.is_set())

    async def test_set_is_idempotent(self):
        api = SyncAsyncliteEvents()
        event = api.make_event()

        event.set()
        self.assertTrue(event.is_set())

        event.set()
        self.assertTrue(event.is_set())

        await event.wait()
        self.assertTrue(event.is_set())
