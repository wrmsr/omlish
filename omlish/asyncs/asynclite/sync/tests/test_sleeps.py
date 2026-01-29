# @omlish-lite
from .....testing.unittest.asyncs import SyncIsolatedAsyncTestCase
from ..sleeps import SyncAsyncliteSleeps


class TestSync(SyncIsolatedAsyncTestCase):
    async def test_sleep(self):
        await SyncAsyncliteSleeps().sleep(.2)
